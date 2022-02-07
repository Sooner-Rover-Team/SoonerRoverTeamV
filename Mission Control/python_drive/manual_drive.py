import pygame
import socket
import configparser
from math import ceil, floor
from pygame.time import Clock

pygame.joystick.init()

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

for joystick in joysticks:
    print('Found',joystick.get_name())


timer = Clock()
THRESHOLD = 0.08
FPS = 20
config = configparser.ConfigParser()
config.read('config.ini')
HOST = config['DEFAULT']['HOST']
PORT = int(config['DEFAULT']['PORT'])

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

if __name__ == "__main__":
    running = True
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
            L_X = joystick.get_axis(0)
            L_Y = joystick.get_axis(1)
            R_X = joystick.get_axis(2)
            R_Y = joystick.get_axis(3)
            # print('fixed',axistospeed(L_Y))
            if abs(L_Y) > THRESHOLD:
                leftwheels = [axistospeed(L_Y)] * 3
                print('leftwheels',leftwheels)
                # print('L_Y',L_Y)
            if abs(L_X) > THRESHOLD:
                # print('L_X',L_X)
                pass
            if abs(R_Y) > THRESHOLD:
                rightwheels = [axistospeed(R_Y)] * 3
                print('rightwheels',rightwheels)
                # print('R_Y',R_Y)
            if abs(R_X) > THRESHOLD:
                # print('R_X',R_X)
                pass


        data = make_message(leftwheels, rightwheels)
        # print(data)
        s.sendall(data)

        timer.tick(FPS)

pygame.joystick.quit()
pygame.quit()