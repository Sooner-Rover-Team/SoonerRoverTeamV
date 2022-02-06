from time import sleep
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
FPS = 10
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

def axistospeed(wheelspeed):
    return fix((-wheelspeed * 126) + 126)

if __name__ == "__main__":
    running = True
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
            if abs(L_Y) > THRESHOLD:
                print('L_Y',L_Y)
                print('fixed',axistospeed(L_Y))
            if abs(L_X) > THRESHOLD:
                print('L_X',L_X)
            if abs(R_Y) > THRESHOLD:
                print('R_Y',R_Y)
            if abs(R_X) > THRESHOLD:
                print('R_X',R_X)

        # s.sendall(data)

        timer.tick(FPS)

pygame.joystick.quit()
pygame.quit()