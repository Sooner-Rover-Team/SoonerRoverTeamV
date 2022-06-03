from time import sleep

import os
from libs import ARTracker

tracker = ARTracker.ARTracker(['/dev/video1'], write=False, useYOLO = False) #ARTracker requires a list of camera files

while True:
    tracker.findMarker(1)#, id2 = 1)
    print('Distance (in cm): ', tracker.distanceToMarker)
    print('Angle: ', tracker.angleToMarker)
    sleep(.5)
