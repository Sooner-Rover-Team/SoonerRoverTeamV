import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import sys
from libs import Drive

#TODO: LEDS!
#Gets a list of coordinates from user and drives to them and then tracks the tag
#Set id1 to -1 if not looking for a tag
def drive(rover, id1, id2=-1):
    locations = []
    
    while True:
        coords = [float(item) for item in input("Enter Lat Lon: ").split()]
        if len(coords) != 2:
            print('please input <lat lon>')
            continue
        if coords[0] == -1 and coords[1] == -1:
            break
       
        locations.append(coords)

    found = rover.driveAlongCoordinates(locations,id1, id2)
    
    if id1 != -1:
        rover.trackARMarker(id1, id2)

if __name__ == "__main__":
    del sys.argv[0]
    rover = Drive.Drive(50, sys.argv)

    drive(rover, 0,1)
