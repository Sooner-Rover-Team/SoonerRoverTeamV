import pygame
import socket
import configparser
from math import ceil, floor
import util
from pygame.time import Clock
import os

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
BRIDGE_HOST = config['Connection']['BRIDGE_HOST']
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


elif CONT_CONFIG == 1:
    L_X_AXIS = 0
    L_Y_AXIS = 1
    L_2_AXIS = 2
    R_X_AXIS = 3
    R_Y_AXIS = 4
    R_2_AXIS = 5

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
screen = pygame.display.set_mode((800,600))
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
screen.fill(WHITE)
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
ebox_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
arm_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
science_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
if USING_BRIDGE:
    ebox_socket.connect((BRIDGE_HOST,EBOX_PORT))
    arm_socket.connect((BRIDGE_HOST,ARM_PORT))
    science_socket.connect((BRIDGE_HOST,SCI_PORT))
else:
    ebox_socket.connect((EBOX_HOST,EBOX_PORT))
    arm_socket.connect((ARM_HOST,ARM_PORT))
    science_socket.connect((SCI_HOST,SCI_PORT))

""" ARM SHIT GOES HERE """
claw_closed = False
coord_u = 18.5;       # wrist position
coord_v = 9.5;
phi = 0.0;            # wrist angle
theta = 0.0;
# physical values of arm:
base_rotation = 0;    # between 0 and 180
shoulder_length = 0;
elbow_length = 0;
wrist_rotation = 0.0; # in degrees
wrist_angle = 0.0;

alt_arm_config = False
""" DONT WORRY ABOUT IT """

""" SCICENCE PACKAGE SHIT """
act_dir = 2 # 0 is down, 1 is up, 2 is neither
act_speed = 0
drill_speed = 0
fan_speed = 0
carousel_speed = 0
carousel_turn = 0
""" pretty simple actually """

""" round, basically """
def fix(number):
    return floor(number) if number % 1 <= .5 else ceil(number)

""" turn an axis into a wheel speed """
def axistospeed(axispos):
    return fix((-axispos * 126) + 126)

""" make a wheel message """
def wheel_message(leftwheels, rightwheels):
    msg =  bytearray([0x23, 0x00, 
                    leftwheels[0], leftwheels[1], leftwheels[2], 
                    rightwheels[0], rightwheels[1], rightwheels[2], 0x00])
    msg[8] = sum(msg[2:8]) & 0xff
    return msg

""" make an arm message """
def arm_messge(claw_dir, base_rotation, shoulder_length, elbow_length, wrist_rotation, wrist_angle):
    out = []
    out.append(255)
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
def sci_message(act_dir, act_speed, drill_speed, fan_speed, carousel_speed, carousel_turn):
    msg = bytearray(9)
    msg[0] = 0xff
    msg[1] = 2
    msg[2] = act_dir
    msg[3] = act_speed
    msg[4] = drill_speed
    msg[5] = fan_speed
    msg[6] = carousel_speed
    msg[7] = carousel_turn
    msg[8] = sum(msg[2:8]) & 0xff
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
                # switch modes
                if event.button == SELECT:
                    arm_installed = not arm_installed
                    if arm_installed:
                        print('arm selected')
                    else:
                        print('science selected')
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
                    if event.button == A_BUTTON:
                        print('lights')
                        if flash:
                            msg = lights(255,0,0)
                        else:
                            msg = lights(0,0,255)
                        flash = not flash
                        ebox_socket.sendall(msg)
                    if event.button == X_BUTTON:
                        msg = toggle_wheels()
                        ebox_socket.sendall(msg)
                else:
                    if arm_installed:
                        if event.button == X_BUTTON:
                            print('alt config')
                            alt_arm_config = not alt_arm_config
                        elif event.button == A_BUTTON:
                            print('clamp (does nothing lmao)')
                            claw_closed = not claw_closed
                            
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

        """ send messages to move the wheels """
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

            data = wheel_message(leftwheels, rightwheels)

            if (isstopped(leftwheels,rightwheels)):
                if not stopsent or halt:
                    print('sent',data[2:8])
                    ebox_socket.sendall(data)
                    stopsent = True
            else:
                print('sent',data[2:8])
                ebox_socket.sendall(data)
                stopsent = False
                
        # send message to move the arm
        elif mode == 'operate' and arm_installed:
            """ ALL OF THIS CODE WAS COPIED FROM THE OLD ARM CODE """
            """ WE DONT HAVE TIME TO UNDERSTAND IT RN, ALL IT NEEDS """
            """ TO DO IS WORK """
            movement_factor = 0.2 / (FPS/10)
            temp_u = coord_u
            temp_v = coord_v
            if(abs(L_Y) > THRESHOLD_HIGH):
                temp_v -= L_Y*movement_factor
            if(abs(L_X) > THRESHOLD_HIGH):
                temp_u -= -L_X*movement_factor
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

            x_len, y_len, temp_u, temp_v = util.arm_calc(alt_arm_config, temp_u, temp_v)
            shoulder_length = int(round((x_len-9.69)*(95/3.93))+40) & 0xff
            elbow_length = int(round((y_len-9.69)*(95/3.93))+40) & 0xff

            coord_u = temp_u;
            coord_v = temp_v;

            if joystick.get_button(L_BUMPER):
                claw_dir = 0
            elif joystick.get_button(R_BUMPER):
                claw_dir = 2
            else:
                claw_dir = 1
                
            wrist_angle = 127 * theta;
            if (wrist_angle < 10 and wrist_angle > -10):
                wrist_angle = 0
            wrist_rotation = 127 * phi;
            if (wrist_rotation < 10 and wrist_rotation > -10):
                wrist_rotation = 0;

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
            print(out)
            arm_socket.sendall(bytearray(out));
        # send science package messages
        else:
            if (abs(L_Y) > THRESHOLD_HIGH):
                if L_Y < 0:
                    act_dir = 1
                if L_Y > 0:
                    act_dir = 0
                act_speed = 127 + int(abs(L_Y*127))
            else:
                act_dir = 2
                act_speed = 126
            if (R_Y < -THRESHOLD_LOW):
                drill_speed -= int(20 * R_Y)
                drill_speed = 255 if drill_speed > 255 else drill_speed
                print('HIGHER')
            if (R_Y > THRESHOLD_LOW):
                drill_speed -= int(20 * R_Y) if drill_speed != 0 else 0
                drill_speed = 0 if drill_speed < 0 else drill_speed
                print('LOWER')
            drill_speed &= 0xff
            if (L_2 > .04):
                fan_speed -= int(20 * L_2)
                fan_speed = 0 if fan_speed < 0 else fan_speed
            elif (R_2 > .04):
                fan_speed += int(20 * R_2)
                fan_speed = 255 if fan_speed > 255 else fan_speed
            if (joystick.get_button(L_BUMPER)):
                carousel_speed = 70
            elif (joystick.get_button(R_BUMPER)):
                carousel_speed = 110
            else:
                carousel_speed = 90
            if joystick.get_button(A_BUTTON):
                carousel_turn = 1
            else:
                carousel_turn = 0
            fan_speed &= 0xff
            print(act_dir,act_speed,fan_speed,drill_speed, carousel_speed)
            msg = sci_message(act_dir, act_speed, drill_speed, fan_speed, carousel_speed, carousel_turn)
            
            science_socket.sendall(msg)


        claw_x = coord_u
        claw_y = -coord_v
        tp.reset()
        screen.fill(WHITE)
        tp.print(screen,"Mode: ",BLACK)
        if mode == 'drive':
            tp.print(screen,"Drive",RED)
            util.draw_drive_stuff(screen,leftwheels, rightwheels)
        elif arm_installed:
            tp.print(screen,"Arm",RED)
            util.draw_arm_stuff(screen, alt_arm_config, claw_x, claw_y)
        else:
            tp.print(screen,"Science",RED)
            act_speed_draw = act_speed-126 if act_dir == 0 else -(act_speed-126)
            util.draw_science_stuff(screen, (act_speed_draw, fan_speed, drill_speed, carousel_speed), tp)
        tp.println(screen, '',BLACK)

        pygame.display.flip()
        timer.tick(FPS)


pygame.joystick.quit()
pygame.quit()