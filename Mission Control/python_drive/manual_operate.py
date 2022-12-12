import pygame
import socket
import configparser
from math import ceil, floor
import util
from pygame.time import Clock
import os

# this allows the pygame window to accept inputs from the controller while the window is hidden (not in focus)
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

""" Change the current directory so config loads right """
if os.path.dirname(__file__) != '':
    current_folder = os.path.dirname(__file__)
    os.chdir(current_folder)

""" Exit if there is no joystick """
pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    print("no joystick found, exiting")
    exit()
joystick = pygame.joystick.Joystick(0)
print('Found',joystick.get_name())

config = configparser.ConfigParser()
config.read('./config.ini')
USING_BRIDGE = config.getboolean('Connection', 'USING_BRIDGE')
BRIDGE_HOST = config['Connection']['BRIDGE_HOST'] # is this the base station ip ?
EBOX_HOST = config['Connection']['EBOX_HOST']
EBOX_PORT = int(config['Connection']['EBOX_PORT'])
ARM_HOST = config['Connection']['ARM_HOST']
ARM_PORT = int(config['Connection']['ARM_PORT'])
SCI_HOST = config['Connection']['SCI_HOST']
SCI_PORT = int(config['Connection']['SCI_PORT'])
CONT_CONFIG = int(config['Controller']['CONFIG'])

""" Define axes and button numbers for different controllers """

if CONT_CONFIG == 0:
    L_X_AXIS = 0
    L_Y_AXIS = 1
    R_X_AXIS = 2
    R_Y_AXIS = 3
    L_2_AXIS = 4
    R_2_AXIS = 5
    gimbal = 0


elif CONT_CONFIG == 1:
    L_X_AXIS = 0
    L_Y_AXIS = 1
    L_2_AXIS = 2
    R_X_AXIS = 3
    R_Y_AXIS = 4
    R_2_AXIS = 5
    gimbal = 0

A_BUTTON = 0
B_BUTTON = 1
X_BUTTON = 2
Y_BUTTON = 3
L_BUMPER = 4
R_BUMPER = 5
SELECT = 6
START = 7

""" Pygame stuff """
pygame.init()
wheelImage = pygame.image.load("backgroundPics\wheelBackground.png")
scienceImage = pygame.image.load("backgroundPics\scienceBackground.png")
armImage = pygame.image.load("backgroundPics\\armBackground.png")
screen = pygame.display.set_mode((1200,600)) # width/ height of window in pixels
image = wheelImage
screen.blit(image, (0,0))
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
#screen.fill(WHITE)
timer = Clock()
tp = util.TextPrint(40)
# pygame.event.set_grab(True)

""" Other constants and global variables """
THRESHOLD_LOW = 0.08
THRESHOLD_HIGH = 0.15
FPS = 20
flash = False
mode = 'drive'
arm_installed = False

""" Socket stuff """
ebox_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # a remote socket where the IP/port are the ones on the microcontroller
arm_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
science_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
if USING_BRIDGE:
    ebox_socket.connect((BRIDGE_HOST,EBOX_PORT)) # What is the bridge? The base station/rover antenna connection?
    arm_socket.connect((BRIDGE_HOST,ARM_PORT))
    science_socket.connect((BRIDGE_HOST,SCI_PORT))
else:
    ebox_socket.connect((EBOX_HOST,EBOX_PORT)) # if not using base station, make the microcontroller the host? why not laptop?
    arm_socket.connect((ARM_HOST,ARM_PORT))
    science_socket.connect((SCI_HOST,SCI_PORT))

""" ARM SHIT GOES HERE """
claw_closed = False
coord_u = 18.5       # wrist position
coord_v = 9.5
phi = 0.0            # wrist angle
theta = 0.0
poke=False
# physical values of arm:
base_rotation = 0    # between 0 and 180
shoulder_length = 0
elbow_length = 0
wrist_rotation = 0.0 # in degrees
wrist_angle = 0.0

alt_arm_config = False
""" DONT WORRY ABOUT IT """

""" SCICENCE PACKAGE SHIT """
# 0 is down, 1 is up, 2 is neither
act_speed = 0
carousel_turn = 0
microscope_position = 0
claw_position = 0

old_act_speed = 0
old_carousel_turn = 0
old_claw_position = 0
old_microscope_position = 0
""" pretty simple actually """

""" round, basically """
def fix(number):
    return floor(number) if number % 1 <= .5 else ceil(number)

""" turn an axis into a wheel speed """
def axistospeed(axispos):
    return fix((-axispos * 126) + 126)

""" make a wheel message """
def wheel_message(leftwheels, rightwheels, gimbalVert, gimbalHoriz):
    msg =  bytearray([0x23, 0x00, # 0b00100011, 0b00000000
                    leftwheels[0], leftwheels[1], leftwheels[2], 
                    rightwheels[0], rightwheels[1], rightwheels[2], gimbalVert, gimbalHoriz, 0x00])
    msg[10] = sum(msg[2:10]) & 0xff # check sum, the & 0xff is to force the checksum to be a 8 bit num 0-256.
    return msg
""" make an arm message """
def arm_messge(claw_dir, base_rotation, shoulder_length, elbow_length, wrist_rotation, wrist_angle):
    out = []
    out.append(255) # 0b11111111
    out.append(1)
    out.append(int(base_rotation) & 0xff)
    out.append(shoulder_length)
    out.append(elbow_length)
    out.append(int(wrist_angle) & 0xff)
    out.append(int(wrist_rotation) & 0xff)
    out.append(claw_dir)
    out.append(int(sum(out[2:8])) & 0xff)
    return out

""" make a science message """
# SCIENCE msg: [startByte, deviceID, linearActuator, carousel, claw, microscope, checkSum]
def sci_message(act_speed, carousel_turn, claw_position, microscope_position):
    msg = bytearray(7)
    msg[0] = 0xff
    msg[1] = 2
    msg[2] = act_speed
    msg[3] = carousel_turn
    msg[4] = claw_position
    msg[5] = microscope_position
    msg[6] = sum(msg[2:8]) & 0xff
    return msg

""" wheel toggle message """
def toggle_wheels():
    msg = bytearray([0x23,0x01])
    print('wheels toggled')
    return msg

""" check if stop is being sent to the wheels"""
def isstopped(leftwheels,rightwheels):
    for s in leftwheels:
        if s != 126:
            return 0
    for s in rightwheels:
        if s != 126:
            return 0
    return 1

""" send a message to the LED strip"""
def lights(r,g,b):
    msg = bytearray(5)
    msg[0] = 0x23
    msg[1] = 0x02
    msg[2] = r & 0xff
    msg[3] = g & 0xff
    msg[4] = b & 0xff
    print(msg)
    return msg

def draw_science_stuff(act_dir,act_speed,fan_speed,drill_speed, carousel_speed):
    w,h = screen.get_size()
    c_x = w/2
    c_y = h/2

def messageIsDifferent(act_speed, carousel_turn, claw_position, microscope_position):
    global old_act_speed
    global old_carousel_turn
    global old_claw_position
    global old_microscope_position
    if ((old_act_speed != act_speed) or (old_carousel_turn != carousel_turn) or (old_claw_position != claw_position) or (old_microscope_position != microscope_position)):
        old_act_speed = act_speed
        old_carousel_turn = carousel_turn
        old_claw_position = claw_position
        old_microscope_position = microscope_position
        return True

if __name__ == "__main__":
    running = True
    stopsent = False
    # halt will override stopsent to make it stop moving no matter what
    halt = False
    leftwheels = [126] * 3
    rightwheels = [126] * 3
    ebox_socket.sendall(lights(0, 0, 255))
    while(running):
        """ check all button events """
        for event in pygame.event.get():
            if event.type == pygame.JOYHATMOTION:
                gim = joystick.get_hat(gimbal)
                msg = wheel_message(leftwheels, rightwheels, gim[0]+1, gim[1]+1)
                ebox_socket.sendall(msg)

            if event.type == pygame.KEYDOWN:
                kp = pygame.key.get_pressed()
                if kp[pygame.K_ESCAPE]:
                    running = False
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.JOYDEVICEREMOVED:
                print('joystick disconnected')
                joystick.quit()
            if event.type == pygame.JOYDEVICEADDED:
                print('joystick connected')
                joystick = pygame.joystick.Joystick(0)
            if event.type == pygame.JOYBUTTONDOWN:
                # switch between science/arm in operate mode
                if event.button == SELECT:
                    arm_installed = not arm_installed
                    if arm_installed:
                        print('arm selected')
                    else:
                        print('science selected')
                # switch between drive and operate modes
                if event.button == B_BUTTON:
                    if mode == 'drive':
                        mode = 'operate'
                        print('mode has been changed to operate')
                        msg = wheel_message([126]*3,[126]*3, 1, 1)
                        ebox_socket.sendall(msg)
                        print('sent',msg[2:8])
                        stopsent = True
                    else:
                        mode = 'drive'
                        print('mode has been changed to drive')
                        ebox_socket.sendall(lights(0,0,255))
                if mode == 'drive':
                    print("drive mode")
                    # A in drive mode will turn lights blue/red
                    if event.button == A_BUTTON:
                        print('lights')
                        if flash:
                            msg = lights(255,0,0)
                        else:
                            msg = lights(0,0,255)
                        flash = not flash
                        ebox_socket.sendall(msg)
                    if event.button == X_BUTTON:
                        print('toggleWheels')
                        msg = toggle_wheels()
                        ebox_socket.sendall(msg)
                else:
                    if arm_installed:
                        if event.button == X_BUTTON:
                            print('alt config')
                            alt_arm_config = not alt_arm_config
                        elif event.button == A_BUTTON:
                            print('claw toggled')
                            claw_closed = not claw_closed
                    else:
                        if event.button == A_BUTTON:
                            if claw_position == 180:
                                claw_position = 0
                            else:
                                claw_position = 180
                            
        """ if the joystick is disconnected wait """
        if pygame.joystick.get_count() == 0:
            continue
        """ also quit if start and select are pressed """
        if joystick.get_button(SELECT) and joystick.get_button(START):
            running = False

        """ assign axes based on controller config """
        L_X = joystick.get_axis(L_X_AXIS)
        L_Y = joystick.get_axis(L_Y_AXIS)
        R_X = joystick.get_axis(R_X_AXIS)
        R_Y = joystick.get_axis(R_Y_AXIS)
        L_2 = joystick.get_axis(L_2_AXIS)
        R_2 = joystick.get_axis(R_2_AXIS)
        gim = joystick.get_hat(gimbal) # size 2, gim[0]= left/right, gim[1]= up/down

        """ Generate msgs from controller input and send messages to designated subsystem """
        # send message to move the wheels
        if mode == 'drive':
            # print('fixed',axistospeed(L_Y))
            if abs(L_Y) > THRESHOLD_LOW:
                leftwheels = [axistospeed(L_Y)] * 3
            else:
                leftwheels = [126] * 3
            if abs(L_X) > THRESHOLD_LOW:
                # left stick x value, unused for rn
                pass
            if abs(R_Y) > THRESHOLD_LOW:
                # wheel #4 is the only one that needed to be reversed somehow
                rightwheels = [axistospeed(R_Y)] * 3
            else:
                rightwheels = [126] * 3
            if abs(R_X) > THRESHOLD_LOW:
                # right stick x value, unused for rn
                pass
            if joystick.get_button(L_BUMPER):
                leftwheels[1:3] = [126] * 2
                rightwheels[1:3] = [126] * 2
            if joystick.get_button(R_BUMPER):
                leftwheels[0:2] = [126] * 2
                rightwheels[0:2] = [126] * 2
            if joystick.get_button(L_BUMPER) and joystick.get_button(R_BUMPER):
                halt = True
                leftwheels[0:3] = [126] * 3
                rightwheels[0:3] = [126] * 3
            else:
                halt = False

            data = wheel_message(leftwheels, rightwheels, gim[0]+1, gim[1]+1) #gim+1 to avoid sending negative #s

            if (isstopped(leftwheels,rightwheels)):
                if not stopsent or halt:
                    print('sent',data[2:10])
                    ebox_socket.sendall(data)
                    stopsent = True
            else:
                print('sent',data[2:10])
                ebox_socket.sendall(data)
                stopsent = False
                
        # send message to move the arm
        elif mode == 'operate' and arm_installed:
            """ ALL OF THIS CODE WAS COPIED FROM THE OLD ARM CODE """
            """ WE DONT HAVE TIME TO UNDERSTAND IT RN, ALL IT NEEDS """
            """ TO DO IS WORK """
            # TODO: Make functions to cut power in wrist/ keeping it down for pickin up heavy things?
            # TODO: Improve GUI to show control layouts.
            # TODO: Make function for smooth "poking" motion for button pressing

            # movement factor is some rate that the position values change?
            movement_factor = 0.2 / (FPS/10)
            # temporarly save coords to do inverse kinematics on the moved point
            temp_u = coord_u
            temp_v = coord_v

            # if Y button is pressed when controlling the arm, arm performs 'poking' action for buttons
            #    button can be held down to keep arm extended
            # if(joystick.get_button(Y_BUTTON) and not poke):
            #     poke=True
            #     temp_u += 1*movement_factor
            # elif(not joystick.get_button(Y_BUTTON) and poke):
            #     poke = False
            #     temp_u -= 1*movement_factor

            if(joystick.get_button(Y_BUTTON)):
                temp_u += 1*movement_factor
                temp_v += .5*movement_factor


            # left stick moves point in space left/right/up/down
            if(abs(L_Y) > THRESHOLD_HIGH):
                temp_v -= L_Y*movement_factor
            if(abs(L_X) > THRESHOLD_HIGH):
                temp_u -= -L_X*movement_factor
            # right joystick controls hangle of wrist I think. pitch up/down/left/right
            if(abs(R_X) > THRESHOLD_HIGH):
                theta = -R_X
            else:
                theta = 0
            if(abs(R_Y) > THRESHOLD_HIGH):
                phi = R_Y
            else: 
                phi = 0
            L_2 = (L_2+1)/2
            R_2 = (R_2+1)/2

            # inverse kinematics calculates new GUI points based on new temp_u/temp_v modified by the controller
            x_len, y_len, temp_u, temp_v = util.arm_calc(alt_arm_config, temp_u, temp_v)
            # shoulder/elbow length are distance that actuator should extend
            shoulder_length = int(round((x_len-9.69)*(95/3.93))+40) & 0xff
            elbow_length = int(round((y_len-9.69)*(95/3.93))+40) & 0xff
            # coords for GUI
            coord_u = temp_u
            coord_v = temp_v

            # open/close claw toggle
            if joystick.get_button(L_BUMPER):
                claw_dir = 0
            elif joystick.get_button(R_BUMPER):
                claw_dir = 2
            else:
                claw_dir = 1
            
            # Old wrist control
            wrist_angle = 127 * theta
            if (wrist_angle < 10 and wrist_angle > -10):
                wrist_angle = 0
            wrist_rotation = 127 * phi
            if (wrist_rotation < 10 and wrist_rotation > -10):
                wrist_rotation = 0

            # base speed is controlled by Left/Right Triggers
            if (R_2 > THRESHOLD_LOW and L_2 > THRESHOLD_LOW):
                base_rotation = 90
            elif (L_2 > THRESHOLD_LOW):
                base_rotation = 90 - L_2 * 20
            elif (R_2 > THRESHOLD_LOW):
                base_rotation = 90 + R_2 * 21
            else:
                base_rotation = 90

            # send the data
            out = arm_messge(claw_dir, base_rotation, shoulder_length, elbow_length, wrist_rotation, wrist_angle)
            #print(out)
            arm_socket.sendall(bytearray(out))

        # send science package messages
        # Left/Right bumpers move carousel in sections.
        # Left vertical joystick moves claw up/down
        # Vertical D-pad moves microscope up/down
        # A button toggles claw open/close (might change to right joystick)
        else:
            if (abs(L_Y) > THRESHOLD_HIGH): # left stick vertical axis controls linear actuator -1 to +1. Send 0 to 255. 0-127=backward speed. 127=stop, 127-255=forward speed
                act_speed = 127 + int(L_Y*127)
            else:
                act_speed = 126

            # if (R_Y < -THRESHOLD_LOW): NOT USING DRILL THIS YEAR
            #     drill_speed -= int(20 * R_Y)
            #     drill_speed = 255 if drill_speed > 255 else drill_speed
            #     print('HIGHER')
            # if (R_Y > THRESHOLD_LOW):
            #     drill_speed -= int(20 * R_Y) if drill_speed != 0 else 0
            #     drill_speed = 0 if drill_speed < 0 else drill_speed
            #     print('LOWER')
            # drill_speed &= 0xff

            # if (L_2 > .04): 
            #     fan_speed -= int(20 * L_2) # decrements speed by 20. num can be 0-255. 127 to stop
            #     fan_speed = 0 if fan_speed < 0 else fan_speed # prevents from going below 0
            # elif (R_2 > .04):
            #     fan_speed += int(20 * R_2)
            #     fan_speed = 255 if fan_speed > 255 else fan_speed
            if(abs(gim[1]) > THRESHOLD_HIGH):
                microscope_position += 5*gim[1] #gim[1]=-1 when down d-pad is pressed. +1 when up
                if(microscope_position>180):
                    microscope_position=180
                elif(microscope_position<0):
                    microscope_position=0

            if (joystick.get_button(L_BUMPER)): 
                carousel_turn = 0
            elif (joystick.get_button(R_BUMPER)):
                carousel_turn = 2
            else:
                carousel_turn = 1

            # if joystick.get_button(A_BUTTON):
            #     claw_position=180
            # if joystick.get_button(X_BUTTON):
            #     claw_position = 0

            #print(act_speed, carousel_turn, claw_position, microscope_position)
            if(messageIsDifferent(act_speed, carousel_turn, claw_position, microscope_position)):
                print("a new button is pressed, so a new packet is sent")
                print(act_speed, carousel_turn, claw_position, microscope_position)
                msg = sci_message(act_speed, carousel_turn, claw_position, microscope_position)
                science_socket.sendall(msg)

        """ Generate pyGame gui based on inputs from controller """
        claw_x = coord_u
        claw_y = -coord_v
        tp.reset()
        #screen.fill(WHITE)
        # choose which background is displayed
        if mode == 'drive':
            image = wheelImage
        elif arm_installed:
            image = armImage
        else:
            image = scienceImage

        screen.blit(image, (0,0))
        tp.print(screen,"Mode: ",BLACK)
        if mode == 'drive':
            tp.print(screen,"Drive",RED)
            util.draw_drive_stuff(screen,leftwheels, rightwheels)
        elif arm_installed:
            tp.print(screen,"Arm",RED)
            util.draw_arm_stuff(screen, alt_arm_config, claw_x, claw_y)
        else:
            tp.print(screen,"Science",RED)
            #act_speed_draw = act_speed-126 if act_dir == 0 else -(act_speed-126)
            #util.draw_science_stuff(screen, (act_speed_draw, fan_speed, drill_speed, carousel_speed), tp)
        tp.println(screen, '',BLACK)

        pygame.display.flip()
        timer.tick(40) #FPS - Test once subsystems are built to see how fast we can send messages without big errors or stalls in the arduino function


pygame.joystick.quit()
pygame.quit()