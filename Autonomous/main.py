import os
path = (os.path.dirname(os.path.abspath(__file__)))
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
argParser.add_argument("-id", "--ids", type=int, help="takes either 1 or 2 id values, defaults to -1 if id not assigned", nargs='+')
argParser.add_argument("-ll", "--latLong", type=str, help="takes a filename for a text file, then reads that file for latlong coordinates")
args = argParser.parse_args()
#Gets a list of coordinates from user and drives to them and then tracks the tag
#Set id1 to -1 if not looking for a tag
def drive(rover):
    global flashing
    idList = [-1,-1]
    locations = []

    if args.ids is not None:
        for i in range(len(args.ids)):
            idList[i] = args.ids[i]
    
    id1 = idList[0]
    id2 = idList[1]

    if args.latLong is not None:
        with open(args.latLong) as f:
            lineNum = 0
            for line in f:
                lineNum += 1
                try:
                    coords = [float(item.replace('\ufeff',"")) for item in line.strip().split()]
                except:
                    print("Parse Error on line " + str(lineNum) + ": Please enter <lat long>")
                    break
                else:
                    if len(coords) != 2:
                        print("Error on line " + str(lineNum) + ": Insufficient number of coordinates. Please enter <lat long>")
                        break        
                    locations.append(coords)
            f.close()

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
    
    drive(rover)