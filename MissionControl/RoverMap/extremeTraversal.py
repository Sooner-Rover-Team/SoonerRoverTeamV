from nis import maps
import os
from random import randint, random

from scipy import rand
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import threading

from server import MapServer
from libs import Location

if __name__ == '__main__':

    loc = Location.Location('10.0.0.222', '55556')
    print('Starting GPS')
    loc.start_GPS()
    loc.start_GPS_thread()

    mapServer = MapServer()
    mapServer.register_routes()
    mapServer.start()

    def set_interval(func, sec):
        def func_wrapper():
            set_interval(func, sec)
            func()
        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

    def update():
        print("sending update...")
        #mapServer.update_rover_coords([38.4375 + randint(0, 100) / 10000 , -110.8125])
        mapServer.update_rover_coords([loc.latitude, loc.longitude])
    
    set_interval(update, 0.500)

