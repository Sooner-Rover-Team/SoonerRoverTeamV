import pygame
import socket
import configparser
from math import ceil, floor
import os
from Listener import MessageListener # read gps data
# import matplotlib.pyplot as plt
from collections import deque
from datetime import datetime
import select
import threading
import queue
import pickle

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
CONT_CONFIG = config['Controller']['CONFIG'] # change this in config if using a different controller than the old xbox 360

""" Define axes and button numbers for different controllers """

if CONT_CONFIG == 'xbox':
    L_X_AXIS = 0
    L_Y_AXIS = 1
    R_X_AXIS = 2
    R_Y_AXIS = 3
    L_2_AXIS = 4
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
elif CONT_CONFIG == 'ps':
    L_X_AXIS = 0
    L_Y_AXIS = 1
    L_2_AXIS = 4
    R_X_AXIS = 2
    R_Y_AXIS = 3
    R_2_AXIS = 5

    D_UP = 11
    D_DOWN = 12
    D_LEFT = 13
    D_RIGHT = 14
    A_BUTTON = 0
    B_BUTTON = 1
    X_BUTTON = 2
    Y_BUTTON = 3
    L_BUMPER = 10
    R_BUMPER = 9
    SELECT = 4
    START = 6

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

light = 0

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
""" GPS SOCKET """
gps = MessageListener(ip="192.168.1.3", port=5555) # jetson ip/port
gps.start() # creates a new thread to listen to gps data in background
old_data = {"latitude": -1.0, "longitude": -1.0, "bearing": -1.0} # place holder to just keep printing last received gps coords
""" SCIENCE PLOTS """
# ebox_socket.setblocking(False)
# sciencePlots = ScienceSensorPlots(ebox_socket)
# sciencePlots.start()

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
# old values for more efficient data sending
old_base_rotation = 0    
old_shoulder_length = 0
old_elbow_length = 0
old_wrist_rotation = 0
old_wrist_angle = 0
old_claw_dir = 0
lastArmMsg = [old_shoulder_length, old_elbow_length, old_base_rotation, old_wrist_angle, old_wrist_rotation, old_claw_dir]
# arm 
alt_arm_config = 2

""" SCICENCE PACKAGE SHIT """
# 0 is down, 1 is up, 2 is neither
numSameMessages = 0
# old variables are used to more efficiently send UDP by not sending identical messages over and over again which is pointless.
big_actuator=0
drill=0
small_actuator = 0
test_tubes = 0
camera_servo = 90
old_big_actuator = 0
old_drill = 0
old_small_actuator = 0
old_test_tubes = 0
old_camera_servo = 90
panoramic_camera_angles = [30, 90, 150] # L/R bumper cycles through this list
panoramic_index = 1
bumper_pressed = False

lastScienceMsg = [old_big_actuator, old_drill, old_small_actuator, old_test_tubes, old_camera_servo]
""" pretty simple actually """

""" SCIENCE PLOT SHIT"""
peak_threshold = 10  # Adjust as needed
peaks = []
# Data queue for communication between threads
science_data_queue = queue.Queue()

# Function to receive data and update the queue
def receive_data():
    while True:
        data, _ = ebox_socket.recvfrom(1024)
        science_data_queue.put(data.decode("utf-8"))

# Thread for receiving science sensor data
receive_thread = threading.Thread(target=receive_data)
receive_thread.daemon = True
receive_thread.start()

# Queue for receiving data
# data_queue = queue.Queue()
# scienceData = []
# plt.figure()

# Start the thread to receive data
# receive_thread = threading.Thread(target=receive_data, args=(sock, data_queue))
# receive_thread.daemon = True
# receive_thread.start()
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
                    rightwheels[0], leftwheels[1], rightwheels[2], 0x00])
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
# OLD SCIENCE msg: [startByte, deviceID, linearActuator, carousel, claw, microscope, checkSum]
 # MSG: [0x03, big_actuator, drill, small_actuator, test_tubes, camera_servo, checkSum]
def sci_message(big_actuator, drill, small_actuator, test_tubes, camera_servo):
    msg = bytearray(7)
    msg[0] = 0x03 # ID for SCIENCE
    msg[1] = big_actuator
    msg[2] = drill
    msg[3] = small_actuator
    msg[4] = test_tubes
    msg[5] = camera_servo
    msg[6] = sum(msg[1:6]) & 0xff
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
    return int(toLow + (valueScaled * rightSpan))

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
                # gim = joystick.get_hat(gimbal)
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
                        if light == 0:
                            msg = lights(0,0,0)
                        elif light == 1:
                            msg = lights(255,0,0)
                        elif light == 2:
                            msg = lights(0,255,0)
                        elif light == 3:
                            msg = lights(0,0,255)
                        elif light == 4:
                            msg = lights(255,255,0)
                        elif light == 5:
                            msg = lights(255,0,255)
                        elif light == 6:
                            msg = lights(0,255,255)
                        elif light == 7:
                            msg = lights(255,255,255)
                        light += 1
                        light = light % 8

                        # if flash:
                        #     msg = lights(255,0,0)
                        # else:
                        #     msg = lights(0,0,255)
                        # flash = not flash
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
                        pass
                        # if event.button == A_BUTTON:
                        #     if claw_position == 180:
                        #         claw_position = 90
                        #     else:
                        #         claw_position = 180
                            
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
        if CONT_CONFIG == 'xbox':
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

            # FRONT_MULT = 1.4


            # leftwheels[0] -= 126
            # leftwheels[0] *= FRONT_MULT
            # leftwheels[0] = int(leftwheels[0]) + 126

            # if leftwheels[0] > 252:
            #     leftwheels[0] = 252
            # elif leftwheels[0] < 0:
            #     leftwheels[0] = 0

            # rightwheels[0] -= 126
            # rightwheels[0] *= FRONT_MULT
            # rightwheels[0] = int(rightwheels[0]) + 126

            if rightwheels[0] > 252:
                rightwheels[0] = 252
            elif rightwheels[0] < 0:
                rightwheels[0] = 0


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
                wrist_angle = 126 + int(R_Y * 42) # for fine mainupulation change this to 32 (currently 55)
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
            """ SCIENCE PACKAGE SECTION ---- MSG: [0x03, big_actuator, drill, small_actuator, test_tubes, camera_servo, checkSum] """
        else:
            """ BIG ACTUATOR -> Left Joystick y-axis """ 
            if (abs(L_Y) > THRESHOLD_HIGH): # left stick vertical axis controls linear actuator -1 to +1. Send 0 to 255. 0-127=backward speed. 127=stop, 127-255=forward speed
                big_actuator = 126 - int(L_Y*126)
            else:
                big_actuator = 126

            """ DRILL -> Left/Right Trigger """ # Left bumper (reverse drill) and Right trigger (forward drill) control speeds
            if(L_2 > -1+THRESHOLD_LOW):
                drill = 126 + int((L_2+1)*63)
            elif(R_2 > -1+THRESHOLD_LOW):
                drill = 126 - int((R_2+1)*63)
            else:
                drill = 126

            """ SMALL ACTUATOR ->  Y and A buttons """ # Triangle retracts, cirlce extends (to collect regolith below surface)
            if (joystick.get_button(Y_BUTTON)):
                small_actuator = 252 # small actuator moves so slow that we just send max speeds when controlling
            elif (joystick.get_button(A_BUTTON)):
                small_actuator = 0
            else:
                small_actuator = 126 # dont move if neither button is pressed

            """ TEST TUBE ACTUATOR -> y axis d-pad """
            if CONT_CONFIG == 'xbox':
                if(gim[1] > THRESHOLD_HIGH):
                    test_tubes = 252 # test tube actuator moves so slow that we just send max speeds when controlling
                elif(gim[1] < -THRESHOLD_HIGH):
                    test_tubes = 0
                else:
                    test_tubes = 126
            else:
                if(joystick.get_button(D_UP)):
                    test_tubes = 252 # test tube actuator moves so slow that we just send max speeds when controlling
                elif(joystick.get_button(D_DOWN)):
                    test_tubes = 0
                else:
                    test_tubes = 126

            """ CAMERA SERVO -> Left/Right Bumper for set positions,  x-axis d-pad for fine control """           
            # FOR A REGULAR SERVO. This provides incrimental positioning of camera for visibility
            if CONT_CONFIG == 'xbox':
                if(abs(gim[0]) > THRESHOLD_HIGH):
                    camera_servo += 3*gim[0] # pressing d-pad modifies the current servo position
            else:
                if(joystick.get_button(D_LEFT)):
                    camera_servo -= 3 # pressing d-pad modifies the current servo position   
                elif(joystick.get_button(D_RIGHT)):
                    camera_servo += 3

            if(camera_servo>180):
                camera_servo=180
            elif(camera_servo<0):
                camera_servo=0

            # Left bumper cycles back in panoramic angles. this provides set angles for camera panorama
            elif (joystick.get_button(L_BUMPER)):
                if not bumper_pressed:
                    panoramic_index = (panoramic_index + 1)
                    if panoramic_index > len(panoramic_camera_angles)-1:
                        panoramic_index = len(panoramic_camera_angles)-1
                    
                    camera_servo = panoramic_camera_angles[panoramic_index]
                    bumper_pressed = True
            # Right bumper cycles forward in panormic angles
            elif (joystick.get_button(R_BUMPER)):
                if not bumper_pressed:
                    panoramic_index = (panoramic_index - 1)
                    if panoramic_index < 0:
                        panoramic_index = 0
                    camera_servo = panoramic_camera_angles[panoramic_index]
                bumper_pressed = True
            else:
                bumper_pressed = False

            # If a new button was pressed, then the message is new, meaning new commands need to be sent to rover. If msg hasn't changed, no need to send redundant data
            if(messageIsDifferent([big_actuator, drill, small_actuator, test_tubes, camera_servo], lastScienceMsg) or numSameMessages > 5):
                numSameMessages = 0
                data = sci_message(big_actuator, drill, small_actuator, test_tubes, camera_servo)
                print(big_actuator, drill, small_actuator, test_tubes, camera_servo, data[6])
                ebox_socket.sendall(data)
            else:
                numSameMessages+=1
            # THIS SENDS MSGS REALLY FAST AND SLOWS DOWN THE ARDUINO NANO CAUSING DELAY, LEAVE UNTIL SWITCH TO TEENSY
            # msg = sci_message(act_speed, carousel_turn, claw_position, microscope_position)
            # print(act_speed, carousel_turn, claw_position, microscope_position)
            # print(msg)
            # ebox_socket.sendall(msg)
                
        """ GENERATE SCIENCE PLOTS"""
        # Receive data and address from the client
        if ebox_socket.fileno() != -1:
            ready_to_read, ready_to_write, exceptional_conditions = select.select([ebox_socket], [], [], 0)  # Number = timeout, 0 -> "nonblocking"
            try:
                scienceData = ebox_socket.recv(1024)
            except socket.error as e:
                print("Socket error:", e)
            print(scienceData)

            if scienceData is not None:
                print(scienceData)
                sensor_values = [byte for byte in scienceData]
                sensor_values = [(9/5) * sensor_values[0] + 32, sensor_values[1], (sensor_values[2] * 256 + sensor_values[3]) - 335]
                print(f"Received message: {sensor_values}")
                # update_plots(len(buffers[0]) + 1, sensor_values)  # Increment the x-axis index
                # Check for peaks
                if max(sensor_values) > peak_threshold:
                    peaks.append((datetime.now(), sensor_values))  # Store timestamp, sensor index, and value of peak
        else:
            sensor_values = [0,0,0]


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
        # data, addr = gps.recvfrom(1024) # 1024 is buffer size for max msg length we can get
        # gps_info = [(data[0], data[1]), data[2]]
            # Location information
        data = gps.getData()
        print(data)
        if data is None: # returns None if Listener didnt get UDP msgs from jetson
            data = old_data #{"latitude": -1.0, "longitude": -1.0, "bearing": -1.0}
        else:
            data['latitude'] = float(str(round(data['latitude'], 6)))
            data['longitude'] = float(str(round(data['longitude'], 6)))
            data['bearing'] = float(str(round(data['bearing'], 2)))
        old_data = data

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
            util.draw_science_stuff(screen, (big_actuator, small_actuator, test_tubes, drill, camera_servo), sensor_values, [(data["latitude"], data["longitude"]), data["bearing"]], tp)
            # util.draw_science_stuff(screen, (act_speed, microscope_position, claw_position, carousel_turn), tp)

        tp.println(screen, '',BLACK)

        pygame.display.flip()
        timer.tick(40) #FPS 40 - Test once subsystems are built to see how fast we can send messages without big errors or stalls in the arduino function
        # timer.tick() is # of frames in one second

# swift.stop_GPS()
gps.stop()
pygame.joystick.quit()
pygame.quit()
# plt.ioff()  # Turn off interactive mode
# plt.show()