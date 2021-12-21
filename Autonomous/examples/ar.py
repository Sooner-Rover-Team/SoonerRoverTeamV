import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import sys
sys.path.append('../')

from libs import ARTracker

tracker = ARTracker.ARTracker(['/dev/video2'], write=True) #ARTracker requires a list of camera files

for i in range(0,101):
    tracker.findAR(0)
    print('Distance (in cm): ', tracker.distanceToAR)
    print('Angle: ', tracker.angleToAR)
