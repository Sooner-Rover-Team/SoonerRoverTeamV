import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import sys
sys.path.append('../')

# from gps import gps 
from time import sleep
from libs import location

if __name__ == '__main__':
    l = location.Location()
    print('starting gps')
    l.start_GPS()
    print('reading data')
    while True:
        print(l.latitude)
        print(l.longitude)
        sleep(.5)
