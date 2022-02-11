import pygame
import socket
import configparser
from math import ceil, floor
from pygame.time import Clock
import os
from inspect import getsourcefile

pygame.joystick.init()

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

for joystick in joysticks:
    print('Found',joystick.get_name())

def find_config():
    current_folder = os.getcwd().split('/')[-1]
    if current_folder == 'SoonerRoverTeamV':
        os.chdir(os.getcwd() + '/Mission Control/python_drive/')

find_config()

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
    leftwheels = [127] * 3
    rightwheels = [127] * 3
    while(running):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                kp = pygame.key.get_pressed()
                if kp[pygame.K_ESCAPE]:
                    running = False

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
            # print('leftwheels',leftwheels)
                # print('L_Y',L_Y)
            if abs(L_X) > THRESHOLD:
                # print('L_X',L_X)
                pass
            if abs(R_Y) > THRESHOLD:
                rightwheels = [axistospeed(R_Y)] * 3
            else:
                rightwheels = [126] * 3
            # print('rightwheels',rightwheels)
                # print('R_Y',R_Y)
            if abs(R_X) > THRESHOLD:
                # print('R_X',R_X)
                pass


        data = make_message(leftwheels, rightwheels)
        # print(data)
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