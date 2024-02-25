#import sys
#sys.path.append('../')
from gps import gps
from math import cos, radians, degrees, sin, atan2, pi, sqrt, asin
from threading import Thread
from time import sleep

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# Class that computes functions related to location of Rover
class Location:
    def __init__(self, ip, port):
        self.swift_IP = ip
        self.swift_port = port
        self.latitude = 0
        self.longitude = 0
        self.old_latitude = 0
        self.old_longitude = 0
        self.height = 0
        self.time = 0
        self.error = 0
        self.bearing = 0.0
        self.running = True
        self.all_zero = True
        self.wait_time = 1

    def config(self):
        # read from a file, probably configure this to work with
        # ConfigParser because that's ez
        pass

    # Returns distance in kilometers between given latitude and longitude
    def distance_to(self, lat:float, lon:float):
        earth_radius = 6371.301
        delta_lat = (lat - self.latitude) * (pi/180.0)
        delta_lon = (lon - self.longitude) * (pi/180.0)

        a = sin(delta_lat/2) * sin(delta_lat/2) + cos(self.latitude * (pi/180.0)) * cos(lat * (pi/180.0)) * sin(delta_lon/2) * sin(delta_lon/2)
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return earth_radius * c

    # Calculates difference between given bearing to location and current bearing
    # Positive is turn right, negative is turn left
    def bearing_to(self, lat:float, lon:float):
        resultbearing = self.calc_bearing(self.latitude, self.longitude, lat, lon) - self.bearing
        return resultbearing + 360 if resultbearing < -180 else (resultbearing - 360 if resultbearing > 180 else resultbearing)

    # Starts updating fields from the GPS box
    def start_GPS_thread(self):
        self.running = True
        t = Thread(target=self.update_fields_loop, name=(
                'update GPS fields'), args=())
        t.daemon = True
        t.start()

    # Stops updating fields from GPS box
    def stop_GPS_thread(self):
        self.running = False

    def start_GPS(self):
        # connect to it w gps_init
        gps.gps_init(self.swift_IP, self.swift_port)

    def stop_GPS(self):
        self.running = False
        gps.gps_finish()        
    

    def update_fields_loop(self):
        while(self.running):
            if gps.get_latitude() + gps.get_longitude() != 0:
                self.old_latitude = self.latitude
                self.old_longitude = self.longitude

                self.latitude = gps.get_latitude()
                self.longitude = gps.get_longitude()
                self.height = gps.get_height()
                self.time = gps.get_time()
                self.error = gps.get_error()
                self.bearing = self.calc_bearing(self.old_latitude, self.old_longitude, self.latitude, self.longitude)
                self.all_zero = False
            else:
                all_zero = True
            # maybe print info or sleep or something idk
            sleep(self.wait_time)
        return

    # Calculates bearing between two points. 
    # (0 is North, 90 is East, +/-180 is South, -90 is West)
    def calc_bearing(self,lat1:float, lon1:float, lat2:float, lon2:float):
        x = cos(lat2 * (pi/180.0)) * sin((lon2-lon1) * (pi/180.0))
        y = cos(lat1 * (pi/180.0)) * sin(lat2 * (pi/180.0)) - sin(lat1 * (pi/180.0)) * cos(lat2 * (pi/180.0)) * cos((lon2-lon1) * (pi/180.0))
        return (180.0/pi) * atan2(x,y)

    # Calculate latitutde and longitude given distance (in km) and bearing (in degrees)
    def get_coordinates(self, distance:float, bearing:float):
        # https://stackoverflow.com/questions/7222382/get-lat-long-given-current-point-distance-and-bearing
        R = 6371.301
        brng = radians(bearing)      # Assuming bearing is in degrees
        d = distance

        lat1 = radians(self.latitude)   # Current lat point converted to radians
        lon1 = radians(self.longitude)  # Current long point converted to radians

        lat2 = asin(sin(lat1)*cos(d/R) + 
                    cos(lat1)*sin(d/R)*cos(brng))
        lon2 = lon1 + atan2(sin(brng)*sin(d/R)*cos(lat1),
                            cos(d/R)-sin(lat1)*sin(lat2))

        return degrees(lat2), degrees(lon2)
    
    def get_bearing(self):
        return self.bearing