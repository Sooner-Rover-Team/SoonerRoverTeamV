import pygame
import socket
import configparser
from math import ceil, floor
import os
""" Change the current directory so config loads right """
if os.path.dirname(__file__) != '':
    current_folder = os.path.dirname(__file__)
    os.chdir(current_folder)

import util
from pygame.time import Clock

# this allows the pygame window to accept inputs from the controller while the window is hidden (not in focus)
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"


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
CONT_CONFIG = int(config['Controller']['CONFIG']) # change this in config if using a different controller than the old xbox 360

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
image = wheelImage

screen = pygame.display.set_mode((1200,600)) # width/ height of window in pixels
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
mode = 'drive' #;'drive'
arm_installed = False # Change to False for science mission
sportMode = False

""" Socket stuff """
ebox_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # a remote socket where the IP/port are the ones on the microcontroller
if USING_BRIDGE:
    ebox_socket.connect((BRIDGE_HOST,EBOX_PORT)) # What is the bridge? The base station/rover antenna connection?
else:
    ebox_socket.connect((EBOX_HOST,EBOX_PORT)) # if not using base station, make the microcontroller the host? why not laptop?

""" ARM SHIT GOES HERE """
claw_closed = False
coord_u = 18.5       # wrist position
coord_v = 9.5
phi = 0.0            # wrist angle
theta = 0.0
poke=False
# physical values of arm:
base_rotation = 0    
shoulder_length = 0
elbow_length = 0
wrist_rotation = 0
wrist_angle = 0
claw_dir = 0

old_base_rotation = 0    
old_shoulder_length = 0
old_elbow_length = 0
old_wrist_rotation = 0
old_wrist_angle = 0
old_claw_dir = 0

lastArmMsg = [old_shoulder_length, old_elbow_length, old_base_rotation, old_wrist_angle, old_wrist_rotation, old_claw_dir]

alt_arm_config = 2
""" DONT WORRY ABOUT IT """

""" SCICENCE PACKAGE SHIT """
# 0 is down, 1 is up, 2 is neither
numSameMessages = 0
act_speed = 127
carousel_turn = 1
microscope_position = 1
claw_position = 90

# old variables are used to more efficiently send UDP by not sending identical messages over and over again which is pointless.
old_act_speed = 0
old_carousel_turn = 0
old_claw_position = 0
old_microscope_position = 0

lastScienceMsg = [old_act_speed, old_carousel_turn, old_claw_position, old_microscope_position]
""" pretty simple actually """

def draw_science_stuff(act_dir,act_speed,fan_speed,drill_speed, carousel_speed):
    w,h = screen.get_size()
    c_x = w/2
    c_y = h/2

""" turn an axis into a wheel speed """
def axistospeed(axispos):
    return fix((-axispos * 126) + 126)

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

""" make a wheel message """
def wheel_message(leftwheels, rightwheels):
    msg =  bytearray([0x01, 0x01, # ID for WHEEL system and secondary ID for actual wheels
                    leftwheels[0], leftwheels[1], leftwheels[2], 
                    rightwheels[0], rightwheels[1], rightwheels[2], 0x00])
    msg[8] = sum(msg[2:8]) & 0xff # check sum, the & 0xff is to force the checksum to be a 8 bit num 0-256.
    return msg

""" make an arm message """
def arm_messge(shoulder_length, elbow_length, base_rotation, wrist_angle, wrist_rotation, claw_dir):
    msg = bytearray(8)
    msg[0] = 0x02 # ID for ARM
    msg[1] = shoulder_length
    msg[2] = elbow_length
    msg[3] = base_rotation
    msg[4] = wrist_angle
    msg[5] = wrist_rotation
    msg[6] = claw_dir
    msg[7] = sum(msg[1:7]) & 0xff
    return msg

""" make a science message """
# SCIENCE msg: [startByte, deviceID, linearActuator, carousel, claw, microscope, checkSum]
def sci_message(act_speed, carousel_turn, claw_position, microscope_position):
    msg = bytearray(6)
    msg[0] = 0x03 # ID for SCIENCE
    msg[1] = act_speed
    msg[2] = carousel_turn
    msg[3] = claw_position
    msg[4] = microscope_position
    msg[5] = sum(msg[1:5]) & 0xff
    return msg

""" send a message to the LED strip"""
def lights(r,g,b):
    msg = bytearray(5)
    msg[0] = 0x01 # ID for WHEEL SYSTEM
    msg[1] = 0x02 # secondary ID for LEDS
    msg[2] = r & 0xff
    msg[3] = g & 0xff
    msg[4] = b & 0xff
    # print(msg)
    return msg

""" round, basically """
def fix(number):
    return floor(number) if number % 1 <= .5 else ceil(number)

# determines if the current msg is different from the last. If equal, no need to send another message and busy up arduinos
def messageIsDifferent(new_values, old_values):
    if new_values != old_values:
        old_values[:] = new_values
        return True
    else:
        return False
    
# this function will remap a value from one range to another. ex: map(5, 0, 10, 0, 100) will return 50
def val_map(value, fromLow, fromHigh, toLow, toHigh):
    # Figure out how 'wide' each range is
    leftSpan = fromHigh - fromLow
    rightSpan = toHigh - toLow

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - fromLow) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return toLow + (valueScaled * rightSpan)

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
                msg = wheel_message(leftwheels, rightwheels)
                ebox_socket.sendall(msg)

            if event.type == pygame.KEYDOWN: # Escape key will end the program
                kp = pygame.key.get_pressed()
                if kp[pygame.K_ESCAPE and mode == 'drive']:
                    running = False
            if event.type == pygame.QUIT and mode == 'drive':
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
                        msg = wheel_message([126]*3,[126]*3)
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
                    if event.button == A_BUTTON: # A button changes lights red/blue
                        print('lights')
                        if flash:
                            msg = lights(255,0,0)
                        else:
                            msg = lights(0,0,255)
                        flash = not flash
                        ebox_socket.sendall(msg)
                    if event.button == X_BUTTON: # X button switches modes
                        print('toggleWheels')
                        msg = toggle_wheels()
                        ebox_socket.sendall(msg)
                    if event.button == Y_BUTTON: # Y button toggles sport mode (max speed)
                        print("Sport Mode = ", sportMode)
                        sportMode = not sportMode
                else:
                    if arm_installed:
                        if event.button == X_BUTTON:
                            print('alt config')
                            if(alt_arm_config == 2):
                                alt_arm_config=0
                            else:
                                alt_arm_config += 1
                        elif event.button == A_BUTTON:
                            print('claw toggled')
                            claw_closed = not claw_closed
                    else:
                        if event.button == A_BUTTON:
                            if claw_position == 180:
                                claw_position = 90
                            else:
                                claw_position = 180
                            
        """ if the joystick is disconnected wait """
        if pygame.joystick.get_count() == 0:
            continue
        """ also quit if start and select are pressed """
        if joystick.get_button(SELECT) and joystick.get_button(START) and mode == 'drive':
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
            else:\
                rightwheels = [126] * 3
            if abs(R_X) > THRESHOLD_LOW:
                # right stick x value, unused for rn
                pass
            if joystick.get_button(L_BUMPER): # Front wheels only
                leftwheels[1:2] = [126] * 2
                rightwheels[1:2] = [126] * 2
            if joystick.get_button(R_BUMPER): # Back wheels only
                leftwheels[0:1] = [126] * 2
                rightwheels[0:1] = [126] * 2
            if joystick.get_button(L_BUMPER) and joystick.get_button(R_BUMPER):
                halt = True
                leftwheels[0:3] = [126] * 3
                rightwheels[0:3] = [126] * 3
            else:
                halt = False
            # if in sport mode, remap the values in each wheel to only max out at half speed (0 / 252 is full speed)
            if sportMode:
                leftwheels = [int(val_map(wheel, 0, 252, 63, 189)) for wheel in leftwheels]
                rightwheels = [int(val_map(wheel, 0, 252, 63, 189)) for wheel in rightwheels]

            data = wheel_message(leftwheels, rightwheels) #gim+1 to avoid sending negative #s
            if (isstopped(leftwheels,rightwheels)):
                if not stopsent or halt:
                    print('sent',str([int(x) for x in data[2:8]]), int(data[8]))
                    ebox_socket.sendall(data)
                    stopsent = True
            else:
                print('sent',str([int(x) for x in data[2:8]]), int(data[8]))
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

            # movement factor is some rate that the position values change
            movement_factor = 0.2 / (FPS/10)
            # temporarly save coords to do inverse kinematics on the moved point
            temp_u = coord_u
            temp_v = coord_v

            # spamming the Y button will slowly move arm forwards to making poking buttons easier
            if(joystick.get_button(Y_BUTTON)):
                temp_u += 1*movement_factor
                temp_v += .5*movement_factor


            # left stick moves point in space left/right/up/down
            if(abs(L_Y) > THRESHOLD_HIGH):
                temp_v -= L_Y*movement_factor
            if(abs(L_X) > THRESHOLD_HIGH):
                temp_u -= -L_X*movement_factor

            # inverse kinematics calculates new GUI points based on new temp_u/temp_v modified by the controller
            shoulder_length, elbow_length, temp_u, temp_v = util.arm_calc(alt_arm_config, temp_u, temp_v)
            # shoulder/elbow length are distance that actuator should extend (between 0 and 180 for servo PWM)
            
            # coords for GUI
            coord_u = temp_u
            coord_v = temp_v

            # open/close claw using L1/R1
            if joystick.get_button(L_BUMPER):
                claw_dir = 0
            elif joystick.get_button(R_BUMPER):
                claw_dir = 252
            else:
                claw_dir = 126

            L_2 = (L_2+1)/2 # L2/R2 map from -1 to 1, this remaps to 0 to 1
            R_2 = (R_2+1)/2
            #rotate the wrist 360 using L2/R2
            if(abs(L_2) > THRESHOLD_LOW):
                wrist_rotation = 126 + int(L_2*52)
            elif(abs(R_2) > THRESHOLD_HIGH):
                wrist_rotation = 126 - int(R_2*52)
            else:
                wrist_rotation = 126
            
            # Right joystick moves base and pitch/ yaw. This way, 
            #    from perspective of the claw, left moves claw left, up moves claw up, etc.
            if(abs(R_X) > THRESHOLD_HIGH):
                base_rotation = 126 + int(R_X * 32)
            else:
                base_rotation = 126
            if (abs(R_Y) > THRESHOLD_HIGH):
                wrist_angle = 126 + int(R_Y * 55)
            else:
                wrist_angle = 126
            
            if messageIsDifferent([shoulder_length, elbow_length, base_rotation, wrist_angle, wrist_rotation, claw_dir], lastArmMsg) or numSameMessages > 5:
                numSameMessages = 0
                #print(shoulder_length, elbow_length, base_rotation, wrist_angle, wrist_rotation, claw_dir)
                data = arm_messge(shoulder_length, elbow_length, base_rotation, wrist_angle, wrist_rotation, claw_dir)
                ebox_socket.sendall(data)
            else:
                numSameMessages += 1



            # send the data
            # information, addr = arm_socket.recvfrom(1024) # 1024 is either num of bytes or num of bits to read from server socket
            # print("\n\n Client recieved: ", information)
            # print("Decoded message: ", information.decode('utf-8'), "\n\n")

        # send science package messages
        # Left/Right bumpers move carousel in sections.
        # Left vertical joystick moves claw up/down
        # Vertical D-pad moves microscope up/down
        # A button toggles claw open/close (might change to right joystick)
        else:
            if (abs(L_Y) > THRESHOLD_HIGH): # left stick vertical axis controls linear actuator -1 to +1. Send 0 to 255. 0-127=backward speed. 127=stop, 127-255=forward speed
                act_speed = 127 + int(L_Y*127)
            else:
                act_speed = 127
            
            # FOR A REGULAR SERVO
            # if(abs(gim[1]) > THRESHOLD_HIGH):
            #     microscope_position -= 5*gim[1] #gim[1]=-1 when down d-pad is pressed. +1 when up
            #     if(microscope_position>180):
            #         microscope_position=180
            #     elif(microscope_position<0):
            #         microscope_position=0
            if(gim[1] < 0):
                microscope_position = 0
            elif(gim[1] > 0):
                microscope_position = 2
            else:
                microscope_position = 1

            if (joystick.get_button(L_BUMPER)): 
                carousel_turn = 0
            elif (joystick.get_button(R_BUMPER)):
                carousel_turn = 2
            else:
                carousel_turn = 1


            #print(act_speed, carousel_turn, claw_position, microscope_position)
            if(messageIsDifferent([act_speed, carousel_turn, claw_position, microscope_position], lastScienceMsg) or numSameMessages > 5):
                numSameMessages = 0
                #print("a new button is pressed, so a new packet is sent")
                #print(act_speed, carousel_turn, claw_position, microscope_position)
                data = sci_message(act_speed, carousel_turn, claw_position, microscope_position)
                print(act_speed, carousel_turn, claw_position, microscope_position)
                ebox_socket.sendall(data)
            else:
                numSameMessages+=1
            # THIS SENDS MSGS REALLY FAST AND SLOWS DOWN THE ARDUINO NANO CAUSING DELAY, LEAVE UNTIL SWITCH TO TEENSY
            # msg = sci_message(act_speed, carousel_turn, claw_position, microscope_position)
            # print(act_speed, carousel_turn, claw_position, microscope_position)
            # print(msg)
            # ebox_socket.sendall(msg)

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
            util.draw_science_stuff(screen, (act_speed, microscope_position, claw_position, carousel_turn), tp)

        tp.println(screen, '',BLACK)

        pygame.display.flip()
        timer.tick(40) #FPS 40 - Test once subsystems are built to see how fast we can send messages without big errors or stalls in the arduino function
        # timer.tick() is # of frames in one second

pygame.joystick.quit()
pygame.quit()