import os
path = (os.path.dirname(os.path.abspath(__file__)))
import sys
import argparse
import configparser
from libs import UDPOut
from libs import Drive
import threading
from time import sleep

mbedIP='10.0.0.101'
mbedPort=1001

flashing = False

def flash():
    while flashing:
        UDPOut.sendLED(mbedIP, mbedPort, 'g')
        sleep(.2)
        UDPOut.sendLED(mbedIP, mbedPort, 'o')
        sleep(.2)

argParser = argparse.ArgumentParser()
argParser.add_argument("cameraInput", type=int, help="takes a number representing which camera to use")
argParser.add_argument("-ll", "--latLong", help="option to input latitude longitude coordinates for an AR code, set to true to trigger loop", action="store_true")
args = argParser.parse_args()
#Gets a list of coordinates from user and drives to them and then tracks the tag
#Set id1 to -1 if not looking for a tag
def drive(rover, id1, id2=-1):
    global flashing
    locations = []

    while args.latLong:
        print("Enter Lat Lon (enter -1 -1 if not looking for tag):", end="")
        coords = [float(item) for item in input("").split()]
        if len(coords) != 2:
            print('please input <lat lon>')
            continue
        if coords[0] == -1 and coords[1] == -1:
            break

    flashing = False
    UDPOut.sendLED(mbedIP, mbedPort, 'r')
    found = rover.driveAlongCoordinates(locations,id1, id2)
    
    if id1 != -1:
        rover.trackARMarker(id1, id2)
    
    flashing=True
    lights = threading.Thread(target=flash)
    lights.start()
    #UDPOut.sendLED(mbedIP, mbedPort, 'g')

if __name__ == "__main__":
    os.chdir(path)
    print(os.getcwd())
    #user input (args from system)
    if args.cameraInput is None:
        print("ERROR: must at least specify one camera")
        exit(-1)
    
    #gets the mbed ip and port
    config = configparser.ConfigParser(allow_no_value=True)
    if not config.read('config.ini'):
        print("DID NOT OPEN CONFIG")
        exit(-2)
    mbedIP = str(config['CONFIG']['MBED_IP'])
    mbedPort = int(config['CONFIG']['MBED_PORT'])

    rover = Drive.Drive(50, args.cameraInput)
#    drive(rover, -1)
#    drive(rover, -1)
#    drive(rover, -1)
   # drive(rover, 1)
    drive(rover, 2)
   # drive(rover, 3)
    drive(rover, 4,5)
