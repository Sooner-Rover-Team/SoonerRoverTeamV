import os
path = (os.path.dirname(os.path.abspath(__file__)))
import sys
import configparser
from libs import UDPOut
from libs import Drive

mbedIP='0.0.0.0'
mbedPort=80

#Gets a list of coordinates from user and drives to them and then tracks the tag
#Set id1 to -1 if not looking for a tag
def drive(rover, id1, id2=-1):
    locations = []
    while True:
        print("Enter Lat Lon: ", end="")
        coords = [float(item) for item in input("").split()]
        if len(coords) != 2:
            print('please input <lat lon>')
            continue
        if coords[0] == -1 and coords[1] == -1:
            break
       
        locations.append(coords)

    UDPOut.sendLED(mbedIP, mbedPort, 'r')
    found = rover.driveAlongCoordinates(locations,id1, id2)
    
    if id1 != -1:
        rover.trackARMarker(id1, id2)
    UDPOut.sendLED(mbedIP, mbedPort, 'g')

if __name__ == "__main__":
    os.chdir(path)
    print(os.getcwd())
    del sys.argv[0]
    if(len(sys.argv) < 1):
        print("ERROR: must at least specify one camera")
        exit(-1)
    
    #gets the mbed ip and port
    config = configparser.ConfigParser(allow_no_value=True)
    if not config.read('config.ini'):
        print("DID NOT OPEN CONFIG")
        exit(-2)
    mbedIP = str(config['CONFIG']['MBED_IP'])
    mbedPort = int(config['CONFIG']['MBED_PORT'])

    rover = Drive.Drive(50, sys.argv)
#    drive(rover, -1)
#    drive(rover, -1)
#    drive(rover, -1)
    drive(rover, 1)
    drive(rover, 2)
    drive(rover, 3)
    drive(rover, 4,5)
