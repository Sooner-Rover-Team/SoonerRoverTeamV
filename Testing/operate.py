import os
import pygame
import socket
import configparser
import util
from pygame.time import Clock

# pygame and joystick setup
pygame.init()
pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    print("NO JOYSTICK FOUND, EXITING")
    exit()
joystick = pygame.joystick.Joystick(0)
print('Joystick Found:', joystick.get_name())
timer = Clock()
tp = util.TextPrint(40)

# GUI stuff
wheelImage = pygame.image.load("backgroundPics/wheelBackground.png")
scienceImage = pygame.image.load("backgroundPics/scienceBackground.png")
armImage = pygame.image.load("backgroundPics/armBackground.png")
image = wheelImage
screen = pygame.display.set_mode((1200, 600))  # width/ height of window in pixels
screen.blit(image, (0, 0))
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Change the current directory so config can load, then read the config
if os.path.dirname(__file__) != '':
    current_folder = os.path.dirname(__file__)
    os.chdir(current_folder)
config = configparser.ConfigParser()
config.read('./config.ini')
USING_BRIDGE = config.getboolean('Connection', 'USING_BRIDGE')
BRIDGE_HOST = config['Connection']['BRIDGE_HOST']
EBOX_HOST = config['Connection']['EBOX_HOST']
EBOX_PORT = int(config['Connection']['EBOX_PORT'])
CONTROLLER = config['Controls']['CONTROLLER']
CONFIGURATION = config['Controls']['CONFIGURATION']

# Keymappings and constants
if CONTROLLER == 'xbox':
    L_X_AXIS = 0
    L_Y_AXIS = 1
    R_X_AXIS = 2
    R_Y_AXIS = 3
    L_T_AXIS = 4
    R_T_AXIS = 5
    A_BUTTON = 0
    B_BUTTON = 1
    X_BUTTON = 2
    Y_BUTTON = 3
    L_BUMPER = 4
    R_BUMPER = 5
    SELECT = 6
    START = 7
elif CONTROLLER == 'ps':
    L_X_AXIS = 0
    L_Y_AXIS = 1
    L_2_AXIS = 4
    R_X_AXIS = 2
    R_Y_AXIS = 3
    R_2_AXIS = 5
    A_BUTTON = 0
    B_BUTTON = 1
    X_BUTTON = 2
    Y_BUTTON = 3
    R_BUMPER = 9
    L_BUMPER = 10
    SELECT = 4
    START = 6

THRESHOLD_LOW = 0.08
THRESHOLD_HIGH = 0.15

lastArmMsg = [0, 0, 0, 0, 0, 0]
claw_closed = False
coord_u = 18.5  # wrist position
coord_v = 9.5
phi = 0.0  # wrist angle
theta = 0.0
poke = False

# physical values of arm:
base_rotation = 0
shoulder_length = 0
elbow_length = 0
wrist_rotation = 0
wrist_angle = 0
claw_dir = 0

# a remote socket where the IP/port are the ones on the microcontroller        !!have Jack explain!!
ebox_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
if USING_BRIDGE:
    ebox_socket.connect((BRIDGE_HOST, EBOX_PORT))
else:
    ebox_socket.connect((EBOX_HOST, EBOX_PORT))

# Read axis values from joysticks and send to REMI
def updateWheels(halt, stopsent):
    L_Y = joystick.get_axis(L_Y_AXIS)
    R_Y = joystick.get_axis(R_Y_AXIS)

    if abs(L_Y) > THRESHOLD_LOW:
        leftwheels = [getWheelSpeed(L_Y)] * 3
    else:
        leftwheels = [126] * 3
    if abs(R_Y) > THRESHOLD_LOW:
        rightwheels = [getWheelSpeed(R_Y)] * 3
    else:
        rightwheels = [126] * 3

    if joystick.get_button(L_BUMPER): # Front wheels only
        leftwheels[1:2] = [126] * 2
        rightwheels[1:2] = [126] * 2
    if joystick.get_button(R_BUMPER): # Back wheels only
        leftwheels[0:1] = [126] * 2
        rightwheels[0:1] = [126] * 2
    if joystick.get_button(L_BUMPER) and joystick.get_button(R_BUMPER):
        halt = True
        if not stopsent:
            print('HALTED')

    data = getWheelMessage(leftwheels, rightwheels) #gim+1 to avoid sending negative #s

    if not isStopped(leftwheels, rightwheels) and not halt:
        print('sent',str([int(x) for x in data[2:8]]), int(data[8]))
        ebox_socket.sendall(data)
        stopsent = False
    elif not stopsent:
        print('sent',str([int(x) for x in data[2:8]]), int(data[8]))
        ebox_socket.sendall(data)
        stopsent = True

    return halt, stopsent, leftwheels, rightwheels


# Checks each element in the wheel message and returns true if all messages are 126 (stop)
def isStopped(leftwheels,rightwheels):
    for i in leftwheels:
        if i != 126:
            return False
    for i in rightwheels:
        if i != 126:
            return False
    return True


def updateArm():
    global coord_u
    global coord_v
    L_Y = joystick.get_axis(L_Y_AXIS)
    L_X = joystick.get_axis(L_X_AXIS)
    R_Y = joystick.get_axis(R_Y_AXIS)
    R_X = joystick.get_axis(R_X_AXIS)
    L_T = joystick.get_axis(L_T_AXIS)
    R_T = joystick.get_axis(R_T_AXIS)
    # movement factor is some rate that the position values change
    movement_factor = 0.2 / (20 / 10) # FPS = 20
     # temporarly save coords to do inverse kinematics on the moved point
    temp_u = coord_u
    temp_v = coord_v

    # spamming the Y button will slowly move arm forwards to making poking buttons easier
    if joystick.get_button(Y_BUTTON):
        temp_u += 1 * movement_factor
        temp_v += 0.5 * movement_factor

    # left stick moves point in space left/right/up/down
    if abs(L_Y) > THRESHOLD_HIGH:
        temp_v -= L_Y * movement_factor
    if abs(L_X) > THRESHOLD_HIGH:
        temp_u -= -L_X * movement_factor

    # inverse kinematics calculates new GUI points based on new temp_u/temp_v modified by the controller
    shoulder_length, elbow_length, temp_u, temp_v = util.arm_calc(CONFIGURATION, temp_u, temp_v)
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

    L_T = (L_T + 1) / 2  # L2/R2 map from -1 to 1, this remaps to 0 to 1
    R_T = (R_T + 1) / 2
    # rotate the wrist 360 using L2/R2
    if abs(L_T) > THRESHOLD_LOW:
        wrist_rotation = 126 + int(L_T * 52)
    elif abs(R_T) > THRESHOLD_HIGH:
        wrist_rotation = 126 - int(R_T * 52)
    else:
        wrist_rotation = 126

    # Right joystick moves base and pitch/ yaw. This way,
    # from perspective of the claw, left moves claw left, up moves claw up, etc.
    if abs(R_X) > THRESHOLD_HIGH:
        base_rotation = 126 + int(R_X * 32)
    else:
        base_rotation = 126

    if abs(R_Y) > THRESHOLD_HIGH:
        wrist_angle = 126 + int(R_Y * 42)  # for fine mainupulation change this to 32 (currently 55)
    else:
        wrist_angle = 126

    if (([shoulder_length, elbow_length, base_rotation, wrist_angle, wrist_rotation, claw_dir] != lastArmMsg) or numSameMessages > 5):
        numSameMessages = 0
        data = getArmMessage(shoulder_length, elbow_length, base_rotation, wrist_angle, wrist_rotation, claw_dir,)
        ebox_socket.sendall(data)
    else:
        numSameMessages += 1

def updateScience():
    return 0

# Converts the axis position to a usable wheel speed
def getWheelSpeed(axispos):
    return util.nearestInteger((-axispos * 126) + 126)

# Converts the left and right wheel speeds into an array of bytes so it can be sent to REMI
def getWheelMessage(leftwheels, rightwheels):
    # ID for WHEEL system and secondary ID for actual wheels
    msg = bytearray([0x01, 0x01, leftwheels[0], leftwheels[1], leftwheels[2], rightwheels[0], rightwheels[1], rightwheels[2], 0x00])
    # check sum, the & 0xff is to force the checksum to be a 8 bit num 0-256.
    msg[8] = sum(msg[2:8]) & 0xff
    return msg

def getArmMessage(shoulder_length, elbow_length, base_rotation, wrist_angle, wrist_rotation, claw_dir):
    msg = bytearray(8)
    msg[0] = 0x02  # ID for ARM
    msg[1] = shoulder_length
    msg[2] = elbow_length
    msg[3] = base_rotation
    msg[4] = wrist_angle
    msg[5] = wrist_rotation
    msg[6] = claw_dir
    msg[7] = sum(msg[1:7]) & 0xFF
    return msg

def stopWheels():
    if mode == 'drive':
        msg = getWheelMessage([126]*3, [126]*3)
        ebox_socket.sendall(msg)
        print('HALTED WHEELS')

mode = 'arm'
arm_installed = True
halt = True
sportmode = False
stopsent = False
running = True
print('\n!!Remi is set to arm operation by default, press START to switch to drive mode or SELECT to switch to science package operation!!\n')

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:  # Escape key will end the program
            if pygame.key.get_pressed() == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.JOYDEVICEREMOVED:
            print('JOYSTICK DISCONNECTED')
            joystick.quit()
        if event.type == pygame.JOYDEVICEADDED & pygame.joystick.get_count() == 0:
            print('Joystick Connected')
            joystick = pygame.joystick.Joystick(0)
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == SELECT:
                if arm_installed:
                    stopWheels()
                    arm_installed = False
                    mode = 'science'
                    print('ARM Uninstalled\nSwitched to SCIENCE mode\n')
                else:
                    stopWheels()
                    arm_installed = True
                    mode = 'arm'
                    print('ARM Installed\nSwitched to ARM mode\n')
            if event.button == START:
                if arm_installed:
                    if mode == 'arm':
                        mode = 'drive'
                        print('Switched to DRIVE mode\n')
                    elif mode == 'drive':
                        stopWheels()
                        mode = 'arm'
                        print('Switched to ARM mode\n')
                else:
                    if mode == 'science':
                        mode = 'drive'
                        print('Switched to DRIVE mode\n')
                    elif mode == 'drive':
                        stopWheels()
                        mode = 'science'
                        print('Switched to SCIENCE mode')
            if event.button == Y_BUTTON and mode == 'drive':
                sportmode = True
                print('\nSPORT MODE ACTIVATED')
    if mode == 'drive':
        halt, stopsent, leftwheels, rightwheels = updateWheels(halt, stopsent)
        halt = False
    elif mode == 'arm' and arm_installed:
        halt = True
        updateArm()
    elif mode == 'science':
        halt = True
        updateScience()
    
    claw_x = coord_u
    claw_y = -coord_v
    tp.reset()

    if mode == "drive":
        image = wheelImage
    elif arm_installed:
        image = armImage
    else:
        image = scienceImage

    screen.blit(image, (0, 0))
    tp.print(screen, "Mode: ", BLACK)
    if mode == "drive":
        tp.print(screen, "Drive", RED)
        util.draw_drive_stuff(screen, leftwheels, rightwheels)
    elif arm_installed:
        tp.print(screen, "Arm", RED)
        util.draw_arm_stuff(screen, CONFIGURATION, claw_x, claw_y)
    else:
        tp.print(screen, "Science", RED)
        #util.draw_science_stuff(screen, (act_speed, microscope_position, claw_position, carousel_turn), tp,)

    tp.println(screen, "", BLACK)

    pygame.display.flip()

pygame.joystick.quit()
pygame.quit()