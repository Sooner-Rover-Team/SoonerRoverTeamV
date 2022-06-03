from time import sleep
from libs import Location

#os.chdir(os.path.dirname(os.path.abspath(__file__)))
if __name__ == '__main__':
    l = Location.Location('10.0.0.222','55556')
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
