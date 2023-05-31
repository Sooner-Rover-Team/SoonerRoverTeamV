from time import sleep

import os
from libs import ARTracker
from signal import SIGINT, signal
tracker = ARTracker.ARTracker([1], write=True, useYOLO = False) #ARTracker requires a list of camera files


while True:
    tracker.findMarker(2)
    print('Distance (in cm): ', tracker.distanceToMarker)
    print('Angle: ', tracker.angleToMarker)

