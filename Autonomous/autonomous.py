# from gps import gps 
from time import sleep
from location.location import Location

if __name__ == '__main__':
    l = Location()
    print('starting gps')
    l.start_GPS()
    print('reading data')
    while True:
        print(l.latitude)
        print(l.longitude)
        sleep(.5)