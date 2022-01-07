#If someone knows a better way to write the next 5 lines, lmk
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import sys
sys.path.append('../')

from libs import ARTracker
from time import sleep

tracker = ARTracker.ARTracker(['/dev/video4'], write=False) #ARTracker requires a list of camera files

while True:
    tracker.findMarker(0)#, id2 = 1)
    print('Distance (in cm): ', tracker.distanceToMarker)
    print('Angle: ', tracker.angleToMarker)
    sleep(.5)
