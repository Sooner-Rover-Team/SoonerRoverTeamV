from time import sleep
import threading
from libs import Drive
from libs import UDPOut
import configparser
import argparse
import os
path = (os.path.dirname(os.path.abspath(__file__))) # root directory of main.py

mbedIP = '10.0.0.101'
mbedPort = 1001

flashing = False


def flash():
    while flashing:
        UDPOut.sendLED(mbedIP, mbedPort, 'g')
        sleep(.2)
        UDPOut.sendLED(mbedIP, mbedPort, 'o')
        sleep(.2)

# command-line arguments
argParser = argparse.ArgumentParser(prog = "main.py", description="The primary program used to control the rover", epilog="https://github.com/Sooner-Rover-Team/")
argParser.add_argument("-ci", "--cameraInput", "--camera", "cameraInput", dest="camera_input", type=int, required="True",
                       help="takes a number representing which camera to use")
argParser.add_argument("-ll", "--latLong", dest="lat_long", type=str,
                       help="takes a filename for a text file, then reads that file for latlong coordinates")
argParser.add_argument("-AR", "--marker", dest="marker", type=int, nargs='+',
                       help="Takes one or two numbers to represent which marker(s) to aim for. Please provide at least one number, with the next separated by a space.")
argParser.add_argument("--version", action="version", version="0.0.0 (25 Feb 2023)")
args = argParser.parse_args()

# extract args
camera_input_number = args.camera_input
lat_long_file_name = args.lat_long
marker = args.marker 


# Gets a list of coordinates from user and drives to them and then tracks the tag
# Set id1 to -1 if not looking for a tag
def drive(rover, id1, id2=-1):
    global flashing
    locations = []

    if lat_long_file_name is not None:
        with open(lat_long_file_name) as f:
            lineNum = 0
            for line in f:
                lineNum += 1
                try:
                    coords = [float(item.replace('\ufeff', ""))
                              for item in line.strip().split()]
                except:
                    print("Parse Error on line " + str(lineNum) +
                          ": Please enter <lat long>")
                    break
                else:
                    if len(coords) != 2:
                        print("Error on line " + str(lineNum) +
                              ": Insufficient number of coordinates. Please enter <lat long>")
                        break
                    locations.append(coords)
            f.close()

    flashing = False
    UDPOut.sendLED(mbedIP, mbedPort, 'r')
    found = rover.driveAlongCoordinates(locations, id1, id2)

    if id1 != -1:
        rover.trackARMarker(id1, id2)

    flashing = True
    lights = threading.Thread(target=flash)
    lights.start()
    # UDPOut.sendLED(mbedIP, mbedPort, 'g')


if __name__ == "__main__":
    os.chdir(path)
    print(os.getcwd())

    # gets the mbed ip and port
    config = configparser.ConfigParser(allow_no_value=True)
    
    if not config.read('config.ini'):
        print("DID NOT OPEN CONFIG")
        exit(-2)
        
    mbedIP = str(config['CONFIG']['MBED_IP'])
    mbedPort = int(config['CONFIG']['MBED_PORT'])

    rover = Drive.Drive(50, camera_input_number)
    if (marker.len == 2):
        drive(rover, marker[0], marker[1])
    else:
        drive(rover, marker[0])
