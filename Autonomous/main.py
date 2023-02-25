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

def flash():                                  #turns on LEDS around the electrical box 
    while flashing:
        UDPOut.sendLED(mbedIP, mbedPort, 'g')
        sleep(.2)
        UDPOut.sendLED(mbedIP, mbedPort, 'o')
        sleep(.2)

argParser = argparse.ArgumentParser() #helps to specify argunements, such as camera input and logitude and latitude in a txt file
argParser.add_argument("cameraInput", type=int, help="takes a number representing which camera to use")
argParser.add_argument("-ll", "--latLong", type=str, help="takes a filename for a text file, then reads that file for latlong coordinates")
args = argParser.parse_args()
#Gets a list of coordinates from user and drives to them and then tracks the tag
#Set id1 to -1 if not looking for a tag
def drive(rover, id1, id2=-1):
    global flashing
    locations = []

    if args.latLong is not None: #essentially opens the txt file for latitude and longitude and lets the user read it
        with open(args.latLong) as f:
            #Parses the file for coordinates
            lineNum = 0
            for line in f:
                lineNum += 1
                try:
                    coords = [float(item.replace('\ufeff',"")) for item in line.strip().split()] #replaces the \ufeff with nothing
                except:
                    print("Parse Error on line " + str(lineNum) + ": Please enter <lat long>") #error handling incase of a parse error
                    break
                else:
                    if len(coords) != 2:
                        print("Error on line " + str(lineNum) + ": Insufficient number of coordinates. Please enter <lat long>")
                        break        
                    locations.append(coords)
            f.close()

    flashing = False #turns off the LEDS
    UDPOut.sendLED(mbedIP, mbedPort, 'r')
    found = rover.driveAlongCoordinates(locations,id1, id2) #sets color to red and drives to the coordinates
    
    if id1 != -1:
        rover.trackARMarker(id1, id2)
    
    flashing=True #turns on the LEDS
    lights = threading.Thread(target=flash)
    lights.start()
    #UDPOut.sendLED(mbedIP, mbedPort, 'g')

if __name__ == "__main__": #main function
    os.chdir(path) #changes the directory to the path
    print(os.getcwd()) #prints the current directory
    #user input (args from system)
    if args.cameraInput is None: #error handling incase of no camera input
        print("ERROR: must at least specify one camera")
        exit(-1) #terminates program
    
    #gets the mbed ip and port
    config = configparser.ConfigParser(allow_no_value=True) #opens the config file
    if not config.read('config.ini'): 
        print("DID NOT OPEN CONFIG") #error handling incase of no config file
        exit(-2)
    mbedIP = str(config['CONFIG']['MBED_IP']) #connecting our embed to the rover which control the microcontrollers in the wheels
    mbedPort = int(config['CONFIG']['MBED_PORT']) #connecting our embed to the rover which control the microcontrollers in the wheels

    rover = Drive.Drive(50, args.cameraInput) #sets the speed of the rover and the camera input
#    drive(rover, -1)
#    drive(rover, -1)
#    drive(rover, -1)
   # drive(rover, 1)
    drive(rover, 2)
   # drive(rover, 3)
    drive(rover, 4,5)
