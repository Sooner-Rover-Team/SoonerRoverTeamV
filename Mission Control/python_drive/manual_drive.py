import pygame
import socket
import configparser
from math import ceil, floor
from pygame.time import Clock
import os
from inspect import getsourcefile

pygame.joystick.init()

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

# list joysticks
for joystick in joysticks:
    print('Found',joystick.get_name())

# change directory to file
current_folder = os.path.dirname(__file__)
os.chdir(current_folder)

timer = Clock()
THRESHOLD = 0.08
FPS = 30

config = configparser.ConfigParser()
config.read('./config.ini')
HOST = config['Connection']['HOST']
PORT = int(config['Connection']['PORT'])
CONT_TYPE = config['Controller']['TYPE']

if CONT_TYPE == 'XboxSeriesX':
    L_X_AXIS = 0
    L_Y_AXIS = 1
    R_X_AXIS = 2
    R_Y_AXIS = 3

elif CONT_TYPE == 'Xbox360':
    L_X_AXIS = 0
    L_Y_AXIS = 1
    R_X_AXIS = 3
    R_Y_AXIS = 4
    L_BUMPER = 4
    R_BUMPER = 5

pygame.init()

# pygame.display.set_mode((800,600))

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((HOST,PORT))

def fix(number):
    return floor(number) if number % 1 <= .5 else ceil(number)

def axistospeed(axispos):
    return fix((-axispos * 126) + 126)

def make_message(leftwheels, rightwheels):
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

if __name__ == "__main__":
    running = True
    stopsent = False
    leftwheels = [126] * 3
    rightwheels = [126] * 3
    while(running):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                kp = pygame.key.get_pressed()
                if kp[pygame.K_ESCAPE]:
                    running = False
            if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                print('wheel toggle')
                msg = toggle_wheels()
                s.sendall(msg)

        for joystick in joysticks:
            if joystick.get_button(6) and joystick.get_button(7):
                running = False
            L_X = joystick.get_axis(L_X_AXIS)
            L_Y = joystick.get_axis(L_Y_AXIS)
            R_X = joystick.get_axis(R_X_AXIS)
            R_Y = joystick.get_axis(R_Y_AXIS)
            # print('fixed',axistospeed(L_Y))
            if abs(L_Y) > THRESHOLD:
                leftwheels = [axistospeed(L_Y)] * 3
            else:
                leftwheels = [126] * 3
            if abs(L_X) > THRESHOLD:
                # left stick x value, unused for rn
                pass
            if abs(R_Y) > THRESHOLD:
                # wheel #4 is the only one that needed to be reversed somehow
                rightwheels = [axistospeed(R_Y), 252-axistospeed(R_Y), axistospeed(R_Y)]
            else:
                rightwheels = [126] * 3
            if abs(R_X) > THRESHOLD:
                # right stick x value, unused for rn
                pass
            if joystick.get_button(L_BUMPER):
                leftwheels[1:3] = [126] * 2
                rightwheels[1:3] = [126] * 2
            if joystick.get_button(R_BUMPER):
                leftwheels[0:2] = [126] * 2
                rightwheels[0:2] = [126] * 2


        data = make_message(leftwheels, rightwheels)

        if (isstopped(leftwheels,rightwheels)):
            if not stopsent:
                print('sent',data[2:8])
                s.sendall(data)
                stopsent = True
        else:
            print('sent',data[2:8])
            s.sendall(data)
            stopsent = False

        timer.tick(FPS)

pygame.joystick.quit()
pygame.quit()