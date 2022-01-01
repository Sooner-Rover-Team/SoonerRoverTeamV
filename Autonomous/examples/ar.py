#If someone knows a better way to write the next 5 lines, lmk
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import sys
sys.path.append('../')

from libs import ARTracker

tracker = ARTracker.ARTracker(['/dev/video4'], write=False) #ARTracker requires a list of camera files

while True:
    tracker.findAR(0)#, id2 = 1)
    print('Distance (in cm): ', tracker.distanceToTag)
    print('Angle: ', tracker.angleToTag)
