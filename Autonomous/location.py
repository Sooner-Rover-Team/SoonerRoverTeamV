import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#import sys
#sys.path.append('../')

# from gps import gps 
from time import sleep
from libs import Location

if __name__ == '__main__':
    l = Location.Location('10.0.0.7','55556')
    print('starting gps')
    l.start_GPS()
    l.start_GPS_thread()
    print('reading data')
    while True:
        print(l.latitude)
        print(l.longitude)
        print('')
#        print(l.bearing)
        sleep(1)
