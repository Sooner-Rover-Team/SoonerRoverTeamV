import sys
sys.path.append('../')

from ardetector import ARTracker

tracker = ARTracker.ARTracker(['/dev/video2']) #ARTracker requires a list of camera files

for i in range(0,101):
    tracker.findAR(0, write=False)
    print('Distance (in cm): ', tracker.distanceToAR)
    print('Angle: ', tracker.angleToAR)
