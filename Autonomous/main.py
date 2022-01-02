#If someone knows a better way to write the next 5 lines, lmk
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from libs import Drive

#TODO: LEDS!
#Gets a list of coordinates from user and drives to them and then tracks the tag
#Set id1 to -1 if not looking for a tag
def drive(rover, id1, id2=-1):
    locations = []
    
    while True:
        lat = int(input("Lat: "))
        lon = int(input("Lon: "))
        
        if lat == -1 and lon == -1:
            break
       
        locations.append([lat, lon])

    found = rover.driveAlongCoordinates(locations,id1, id2)
    
    if id1 != -1:
        rover.trackARMarker(id1, id2)

if __name__ == "__main__":
    rover = Drive.Drive(40, ['/dev/video2'])

    drive(rover, 1)
