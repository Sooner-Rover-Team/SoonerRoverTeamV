from gps import gps 
from time import sleep

if __name__ == '__main__':
    print('starting gps')
    gps.gps_init('127.0.0.1','8080')
    print('reading data')
    while True:
        print(gps.get_latitude())
        print(gps.get_longitude())
        sleep(.5)