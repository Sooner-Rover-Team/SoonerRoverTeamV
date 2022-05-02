import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#import sys
#sys.path.append('../')

# from gps import gps 
from time import sleep
from libs import Locationf9p

if __name__ == '__main__':
    l = Locationf9p.LocationF9P()
    print('starting gps')
    l.start_GPS()
    l.start_GPS_thread()
    print('reading data')
    while True:
        print(l.latitude)
        print(l.longitude)
        print(l.bearing)
        print()
        sleep(1)
