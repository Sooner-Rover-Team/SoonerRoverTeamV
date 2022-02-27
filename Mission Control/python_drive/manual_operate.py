from asyncio import threads
from socketserver import BaseRequestHandler
from sys import base_prefix
from threading import Thread
from random import randint
from time import sleep
import pygame
import socket
import configparser
from math import ceil, floor, hypot, sqrt, cos, atan, acos, pi
from pygame.time import Clock
import os

pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    exit()
joystick = pygame.joystick.Joystick(0)

# list joysticks
# for joystick in joysticks:
print('Found',joystick.get_name())

# change directory to file
current_folder = os.path.dirname(__file__)
os.chdir(current_folder)

timer = Clock()
THRESHOLD_LOW = 0.08
THRESHOLD_HIGH = 0.15
FPS = 20
flash = False

config = configparser.ConfigParser()
config.read('./config.ini')
EBOX_HOST = config['Connection']['EBOX_HOST']
EBOX_PORT = int(config['Connection']['EBOX_PORT'])
ARM_HOST = config['Connection']['ARM_HOST']
ARM_PORT = int(config['Connection']['ARM_PORT'])
CONT_TYPE = config['Controller']['TYPE']

mode = 'drive'

if CONT_TYPE == 'XboxSeriesX':
    L_X_AXIS = 0
    L_Y_AXIS = 1
    R_X_AXIS = 2
    R_Y_AXIS = 3
    L_2_AXIS = 4
    R_2_AXIS = 5
    A_BUTTON = 0
    B_BUTTON = 1
    X_BUTTON = 2
    Y_BUTTON = 3
    L_BUMPER = 4
    R_BUMPER = 5

elif CONT_TYPE == 'Xbox360':
    L_X_AXIS = 0
    L_Y_AXIS = 1
    R_X_AXIS = 3
    R_Y_AXIS = 4
    L_BUMPER = 4
    R_BUMPER = 5

pygame.init()

screen = pygame.display.set_mode((800,600))
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
screen.fill(WHITE)

ebox_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ebox_socket.connect((EBOX_HOST,EBOX_PORT))
arm_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
arm_socket.connect((ARM_HOST,ARM_PORT))

""" ARM SHIT GOES HERE """
CLAW_L_OPEN = 149
CLAW_L_CLOSED = 87
CLAW_R_OPEN = 73
CLAW_R_CLOSED = 28
clawL = CLAW_L_OPEN
clawR = CLAW_R_OPEN;
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

def fix(number):
    return floor(number) if number % 1 <= .5 else ceil(number)

def axistospeed(axispos):
    return fix((-axispos * 126) + 126)

def wheel_message(leftwheels, rightwheels):
    msg =  bytearray([0x23, 0x00, 
                    leftwheels[0], leftwheels[1], leftwheels[2], 
                    rightwheels[0], rightwheels[1], rightwheels[2], 0x00])
    msg[8] = sum(msg[2:8]) & 0xff
    return msg

def toggle_wheels():
    msg = bytearray([0x23,0x01])
    return msg

def isstopped(leftwheels,rightwheels):
    for s in leftwheels:
        if s != 126:
            return 0
    for s in rightwheels:
        if s != 126:
            return 0
    return 1

def lights(r,g,b):
    msg = bytearray(5)
    msg[0] = 0x23
    msg[1] = 0x02
    msg[2] = r & 0xff
    msg[3] = g & 0xff
    msg[4] = b & 0xff
    print(msg)
    return msg

# def police():
#     if flash:
#         msg = lights(255,0,0)
#         ebox_socket.sendall(msg)
#         sleep(.5)
#         msg = lights(0,0,255)
#         ebox_socket.sendall(msg)
#         sleep(.5)

def draw_arm_stuff():
    scale = 12
    origin_x = 150
    origin_y = 375

    #origin
    pygame.draw.line(screen,BLACK,(origin_x-10, origin_y),(origin_x+10, origin_y))
    pygame.draw.line(screen,BLACK,(origin_x, origin_y-10),(origin_x, origin_y+10))

    if not alt_arm_config:
        # bounds for default configuration
        # painter.drawArc(origin_x-30.75*scale, origin_y-30.75*scale, 30.75*scale*2, 30.75*scale*2, -25*16, 80*16);
        r = pygame.rect.Rect(origin_x-30.75*scale, origin_y-30.75*scale, 30.75*scale*2, 30.75*scale*2)
        pygame.draw.arc(screen,BLACK,r, -24*pi/180, 55*pi/180)
        # painter.drawArc(origin_x-18.02*scale, origin_y-18.02*scale, 18.02*scale*2, 18.02*scale*2, -60*16, 90*16);
        r = pygame.rect.Rect(origin_x-18.02*scale, origin_y-18.02*scale, 18.02*scale*2, 18.02*scale*2)
        pygame.draw.arc(screen,BLACK, r, -52*pi/180, 25*pi/180)
        # painter.drawArc((origin.x()+17.8513*scale)-18.01*scale, (origin.y()-2.3858*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -120*16, 70*16);
        r = pygame.rect.Rect((origin_x+17.8513*scale)-18.01*scale, (origin_y-2.3858*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2)
        pygame.draw.arc(screen,BLACK, r, -113*pi/180, -55*pi/180)
        # painter.drawArc((origin_x+1.4631*scale)-18.01*scale, (origin_y-17.9505*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -40*16, 65*16);
        r = pygame.rect.Rect((origin_x+1.4631*scale)-18.01*scale, (origin_y-17.9505*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2)
        pygame.draw.arc(screen,BLACK, r, -36*pi/180, 24*pi/180)
    else:
        # bounds for equipment servicing configuration
        # painter.drawArc(origin_x-30.93*scale, origin_y-30.93*scale, 30.93*scale*2, 30.93*scale*2, -20*pi/180, 90*pi/180);
        r = pygame.rect.Rect(origin_x-30.93*scale, origin_y-30.93*scale, 30.93*scale*2, 30.93*scale*2)
        pygame.draw.arc(screen, BLACK,r, -15*pi/180, 63*pi/180)
        # painter.drawArc(origin_x-20.67*scale, origin_y-20.67*scale, 20.67*scale*2, 20.67*scale*2, -60*pi/180, 90*pi/180);
        r = pygame.rect.Rect(origin_x-20.67*scale, origin_y-20.67*scale, 20.67*scale*2, 20.67*scale*2)
        pygame.draw.arc(screen, BLACK,r, -51*pi/180, 27*pi/180)
        # painter.drawArc((origin_x+14.8678*scale)-18.01*scale, (origin_y-1.9870*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -100*pi/180, 70*pi/180);
        r = pygame.rect.Rect((origin_x+14.8678*scale)-18.01*scale, (origin_y-1.9870*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2)
        pygame.draw.arc(screen, BLACK,r, -96*pi/180, -33*pi/180)
        # painter.drawArc((origin_x+1.2187*scale)-18.01*scale, (origin_y-14.9504*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -20*pi/180, 65*pi/180);
        r = pygame.rect.Rect((origin_x+1.2187*scale)-18.01*scale, (origin_y-14.9504*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2)
        pygame.draw.arc(screen, BLACK,r, -20*pi/180, 45*pi/180)

    #claw position
    pygame.draw.line(screen, BLACK, (origin_x+claw_x*scale-5, origin_y+claw_y*scale-5), (origin_x+claw_x*scale+5, origin_y+claw_y*scale+5))
    pygame.draw.line(screen, BLACK, (origin_x+claw_x*scale-5, origin_y+claw_y*scale+5), (origin_x+claw_x*scale+5, origin_y+claw_y*scale-5))

if __name__ == "__main__":
    running = True
    stopsent = False
    leftwheels = [126] * 3
    rightwheels = [126] * 3
    # t = Thread
    while(running):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                kp = pygame.key.get_pressed()
                if kp[pygame.K_ESCAPE]:
                    running = False
            if event.type == pygame.JOYDEVICEREMOVED:
                print('joystick disconnected')
                joystick.quit()
            if event.type == pygame.JOYDEVICEADDED:
                print('joystick connected')
                joystick = pygame.joystick.Joystick(0)
            if event.type == pygame.JOYBUTTONDOWN:
                # switch modes
                if event.button == B_BUTTON:
                    if mode == 'drive':
                        mode = 'arm'
                        print('mode has been changed to arm')
                        msg = wheel_message([126]*3,[126]*3)
                        ebox_socket.sendall(msg)
                        print('sent',msg[2:8])
                        stopsent = True
                    else:
                        mode = 'drive'
                        print('mode has been changed to drive')
                if mode == 'drive':
                    if event.button == A_BUTTON:
                        print('lights')
                        if flash:
                            msg = lights(255,0,0)
                        else:
                            msg = lights(0,0,255)
                        flash = not flash
                        ebox_socket.sendall(msg)
                else:
                    if event.button == X_BUTTON:
                        print('alt config')
                        alt_arm_config = not alt_arm_config
                    elif event.button == A_BUTTON:
                        print('clamp')
                        if claw_closed:
                            clawL = CLAW_L_OPEN
                            clawR = CLAW_R_OPEN
                        else:
                            clawL = CLAW_L_CLOSED
                            clawR = CLAW_R_CLOSED
                        claw_closed = not claw_closed
        
        if pygame.joystick.get_count() == 0:
            continue
            
        if joystick.get_button(6) and joystick.get_button(7):
            running = False
        L_X = joystick.get_axis(L_X_AXIS)
        L_Y = joystick.get_axis(L_Y_AXIS)
        R_X = joystick.get_axis(R_X_AXIS)
        R_Y = joystick.get_axis(R_Y_AXIS)
        L_2 = joystick.get_axis(L_2_AXIS)
        R_2 = joystick.get_axis(R_2_AXIS)

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

            data = wheel_message(leftwheels, rightwheels)

            if (isstopped(leftwheels,rightwheels)):
                if not stopsent:
                    print('sent',data[2:8])
                    ebox_socket.sendall(data)
                    stopsent = True
            else:
                print('sent',data[2:8])
                ebox_socket.sendall(data)
                stopsent = False

        else:
            # TODO: Figure this shit out
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
                phi = R_X
            else:
                phi = 0
            L_2 = (L_2+1)/2
            R_2 = (R_2+1)/2
            if(abs(R_Y) > THRESHOLD_HIGH):
                theta = -R_Y
            else: theta = 0

            if not alt_arm_config:
                #default configuration
                #make sure it stays in cylindrical bounds:
                # x^2 + y^2 <= 945.7103
                if( hypot(temp_u, temp_v) > 30.75 ):
                    temp_u += temp_u*((30.75/hypot(temp_u, temp_v))-1)
                    temp_v += temp_v*((30.75/hypot(temp_u, temp_v))-1)
                # x^2 + y^2 >= 324.6326
                if( hypot(temp_u, temp_v) < 18.02 ):
                    temp_u += temp_u*((18.02/hypot(temp_u, temp_v))-1)
                    temp_v += temp_v*((18.02/hypot(temp_u, temp_v))-1)
                # (x-17.8513)^2 + (y-2.3858)^2 <= 324.3601 ***only for the bottom part of the circle***
                if( hypot(temp_u-17.8513, temp_v-2.3858) > 18.01 and temp_v < 0 ):
                    temp_u += (temp_u-17.8513)*((18.01/hypot((temp_u-17.8513), (temp_v-2.3858)))-1)
                    temp_v += (temp_v-2.3858)*((18.01/hypot((temp_u-17.8513), (temp_v-2.3858)))-1)
                # (x-1.4631)^2 + (y-17.9505)^2 >= 324.3601
                if( hypot(temp_u-1.4631, temp_v-17.9505) < 18.01 ):
                    temp_u += (temp_u-1.4631)*((18.01/hypot((temp_u-1.4631), (temp_v-17.9505)))-1)
                    temp_v += (temp_v-17.9505)*((18.01/hypot((temp_u-1.4631), (temp_v-17.9505)))-1)

                # calculate the actuator lengths
                hypot2 = pow(temp_u, 2) + pow(temp_v, 2)
                x_len = sqrt(160.6811-77.8123*cos( acos( (99.3601-hypot2)/(-30.0*sqrt(hypot2)) ) + atan(temp_v/temp_u)+.40602 ))
                y_len = sqrt(168.5116-(85.8577*cos(2.91186-acos((hypot2-549.3601)/(-540.3)))))

                # convert inches to degrees for the servos
                # max: 13.62 in = 135 deg
                # min: 9.69 in = 40 deg
                shoulder_length = int(round((x_len-9.69)*(95/3.93))+40) & 0xff
                elbow_length = int(round((y_len-9.69)*(95/3.93))+40) & 0xff

                coord_u = temp_u;
                coord_v = temp_v;
            else: 
                # configuration for the equipment servicing task
                # make sure it stays in cylindrical bounds:
                # x^2 + y^2 <= 956.4557
                if( hypot(temp_u, temp_v) > 30.93 ):
                    temp_u += temp_u*((30.93/hypot(temp_u, temp_v))-1)
                    temp_v += temp_v*((30.93/hypot(temp_u, temp_v))-1)
                # x^2 + y^2 >= 427.3300
                if( hypot(temp_u, temp_v) < 20.67 ):
                    temp_u += temp_u*((20.67/hypot(temp_u, temp_v))-1)
                    temp_v += temp_v*((20.67/hypot(temp_u, temp_v))-1)
                # (x-14.8678)^2 + (y-1.9870)^2 <= 324.3601 ***only for the bottom part of the circle***
                if( hypot(temp_u-14.8678, temp_v-1.9870) > 18.01 and temp_v < 0 ):
                    temp_u += (temp_u-14.8678)*((18.01/hypot((temp_u-14.8678), (temp_v-1.9870)))-1)
                    temp_v += (temp_v-1.9870)*((18.01/hypot((temp_u-14.8678), (temp_v-1.9870)))-1)
                # (x-1.2187)^2 + (y-14.9504)^2 >= 324.3601
                if( hypot(temp_u-1.2187, temp_v-14.9504) < 18.01 ):
                    temp_u += (temp_u-1.2187)*((18.01/hypot((temp_u-1.2187), (temp_v-14.9504)))-1)
                    temp_v += (temp_v-14.9504)*((18.01/hypot((temp_u-1.2187), (temp_v-14.9504)))-1)
                # the collision stuff doesnt work as well at such sharp corners
                if( temp_v > 0 ):
                    if( temp_v > 27.5 ):
                        temp_v = 27.5
                    if( temp_u < 14.25 ):
                        temp_u = 14.25

                # calculate the length of each actuator based on the coordinate (u,v)
                hypot2 = pow(temp_u, 2) + pow(temp_v, 2);
                x_len = sqrt(160.6811-77.8123*cos(acos((99.3601-hypot2)/(-30.0*sqrt(hypot2)))+atan(temp_v/temp_u)+.40602));
                y_len = sqrt(180.5948-(100.9791*cos(2.96241-acos((hypot2-549.3601)/(-540.3)))));

                # convert inches to degrees for the servos
                # max: 13.62 in = 135 deg, min: 9.69 in = 40 deg
                shoulder_length = int(round((x_len-9.69)*(95/3.93))+40) & 0xff;
                elbow_length = int(round((y_len-9.69)*(95/3.93))+40) & 0xff;

                coord_u = temp_u;
                coord_v = temp_v;
                
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
            out = []
            out.append(255);
            out.append(1);
            out.append(int(base_rotation) & 0xff);
            out.append(shoulder_length);
            out.append(elbow_length);
            out.append(int(wrist_angle) & 0xff);
            out.append(int(wrist_rotation) & 0xff);
            out.append(clawL);
            out.append(clawR);
            out.append(int((base_rotation+shoulder_length+elbow_length+wrist_angle+wrist_rotation+clawL+clawR)/7)&0xff);
            print(out)
            out = bytearray(out)
            arm_socket.sendall(out);


        claw_x = coord_u
        claw_y = -coord_v

        screen.fill(WHITE)
        draw_arm_stuff()

        pygame.display.flip()

        timer.tick(FPS)

pygame.joystick.quit()
pygame.quit()