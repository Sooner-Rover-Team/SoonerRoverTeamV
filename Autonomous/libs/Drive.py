from threading import Thread
from threading import Timer
import configparser
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import math
from time import sleep
from nis import maps

import sys
sys.path.append('../../Mission Control/RoverMap/')
from server import MapServer

from libs import UDPOut
from libs import Location
from libs import ARTracker

class Drive:
    
    def __init__(self, baseSpeed, cameras):
        self.baseSpeed = baseSpeed
        self.tracker = ARTracker.ARTracker(cameras)
        
        #Starts everything needed by the map
        self.mapServer = MapServer()
        self.mapServer.register_routes()
        self.mapServer.start(debug=False)
        self.startMap(self.updateMap, .5)
        sleep(.1)

        #sets up the parser
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(os.path.dirname(__file__) + '/../config.ini')
        
        #parses config
        self.mbedIP = str(config['CONFIG']['MBED_IP'])
        self.mbedPort = int(config['CONFIG']['MBED_PORT'])
        swiftIP = str(config['CONFIG']['SWIFT_IP'])
        swiftPort = str(config['CONFIG']['SWIFT_PORT'])
        self.gps = Location.Location(swiftIP, swiftPort)
        self.gps.start_GPS()
        
        self.speeds = [0,0]
        self.errorAccumulation = 0.0
        
        #starts the thread that sends wheel speeds
        self.running = True
        t = Thread(target=self.sendSpeed, name=('send wheel speeds'), args=())
        t.daemon = True
        t.start()

        
    def startMap(self, func, seconds):
        def func_wrapper():
            self.startMap(func, seconds)
            func()
        t = Timer(seconds, func_wrapper)
        t.start()
        return t

    def updateMap(self):
        self.mapServer.update_rover_coords([self.gps.latitude, self.gps.longitude])


    #Every 100ms, send the current left and right wheel speeds to the mbeds
    def sendSpeed(self):
        while self.running:
            ls = int(self.speeds[0])
            rs = int(self.speeds[1])
            UDPOut.sendWheelSpeeds(self.mbedIP, self.mbedPort, ls,ls,ls, rs,rs,rs)
            sleep(.1)
    
    #time in milliseconds
    #error in degrees
    #Gets adjusted speeds based off of error and how long its been off (uses p and i)   
    def getSpeeds(self,speed, error, time, kp = .35, ki=.000035):
        values = [0,0]

        #p and i constants if doing a pivot turn
        if speed == 0:
            kp = .9
            ki = .001

        #Updates the error accumulation
        self.errorAccumulation += error * time

        #Gets the adjusted speed values
        values[0] = speed + (error * kp + self.errorAccumulation * ki)
        values[1] = speed - (error * kp + self.errorAccumulation * ki)

        #Gets the maximum speed values depending if it is pivoting or not
        min = speed  - 30
        max = speed + 30
        if speed == 0:
            max += 40
            min -= 40
        if max > 90:
            max=90
        if min < -90:
            min = -90
            
        #Makes sure the adjusted speed values are within the max and mins
        if values[0] > max:
            values[0] = max
        elif values[0] < min:
            values[0] = min
        if values[1] > max:
            values[1] = max
        elif values[1] < min:
            values[1] = min
       
        #Makes sure the speeds are >10 or <-10. Wheels lock up if the speeds are <10 and >-10
        if values[0] <= 0 and values[0] > -10:
            values[0] = -10
        elif values[0] > 0 and values[0] < 10:
            values[0] = 10
        
        if values[1] <= 0 and values[1] > -10:
            values[1] = -10
        elif values[1] > 0 and values[1] < 10:
            values[1] = 10
        
        if values[0] <= 0 and values[0] > -40 and speed == 0:
            values[0] = -40
        elif values[0] > 0 and values[0] < 40 and speed == 0:
            values[0] = 40
        
        if values[1] <= 0 and values[1] > -40 and speed == 0:
            values[1] = -40
        elif values[1] > 0 and values[1] < 40 and speed == 0:
            values[1] = 40
    
        return values
        
    #Cleaner way to print out the wheel speeds
    def printSpeeds(self):
        print("Left wheels: ", round(self.speeds[0],1))
        print("Right wheels: ", round(self.speeds[1],1))
    
    #Drives along a given list of GPS coordinates while looking for the given ar markers
    #Keep id2 at -1 if looking for one post, set id1 to -1 if you aren't looking for AR markers 
    def driveAlongCoordinates(self, locations, id1, id2=-1):
        #Starts the GPS
        self.gps.start_GPS_thread()
        print('Waiting for GPS connection...')
        #while self.gps.all_zero: 
        #    continue
        print('Connected to GPS')
        
        #backs up and turns to avoid running into the last detected sign. Also allows it to get a lock on heading
        if(id1 > -1):
            self.speeds = [-60,-60]
            self.printSpeeds()
            sleep(2)
            self.speeds = [0,0]
            self.printSpeeds()
            sleep(2)
            self.speeds = [80,20]
            self.printSpeeds()
            sleep(4)
        else:
            self.speeds = (self.baseSpeed, self.baseSpeed)
            self.printSpeeds()
            sleep(3)

        #navigates to each location
        for l in locations:
            self.errorAccumulation = 0
            while self.gps.distance_to(l[0], l[1]) > .0025: #.0025km
                bearingTo = self.gps.bearing_to(l[0], l[1])
                print(self.gps.distance_to(l[0], l[1]) )
                self.speeds = self.getSpeeds(self.baseSpeed, bearingTo, 100) #It will sleep for 100ms
                sleep(.1) #Sleeps for 100ms
                self.printSpeeds()
                
                if(id1 != -1 and self.tracker.findMarker(id1, id2)):
                    self.gps.stop_GPS_thread()
                    print('Found Marker!')
                    self.speeds = [0,0]
                    return True
                    
        self.gps.stop_GPS_thread()
        print('Made it to location without seeing marker(s)')
        self.speeds = [0,0]
        return False
                
    def trackARMarker(self, id1, id2=-1):
        stopDistance = 350 #stops when 250cm from markers TODO make sure rover doesn't stop too far away with huddlys
        timesNotFound = -1
        self.tracker.findMarker(id1, id2, cameras=1) #Gets and initial angle from the main camera
        self.errorAccumulation = 0
           
        count = 0
        #Centers the middle camera with the tag
        while self.tracker.angleToMarker > 14 or self.tracker.angleToMarker < -14:
            if self.tracker.findMarker(id1, id2, cameras=1): #Only looking with the center camera right now
                if timesNotFound == -1:
                    self.speeds = [0,0]
                    sleep(.5)
                    self.speeds = [self.baseSpeed, self.baseSpeed]
                    sleep(.8)
                    self.speeds = [0,0]
                else:
                    self.speeds = self.getSpeeds(0, self.tracker.angleToMarker, 100)
                print(self.tracker.angleToMarker, " ", self.tracker.distanceToMarker)
                timesNotFound = 0
            elif timesNotFound == -1: #Never seen the tag with the main camera
                if(math.ceil(int(count/20)/5) % 2 == 1):
                    self.speeds = [self.baseSpeed+5,-self.baseSpeed-5]
                else:
                    self.speeds = [-self.baseSpeed-5,self.baseSpeed+5]
            elif timesNotFound < 15: #Lost the tag for less than 1.5 seconds after seeing it with the main camera
                timesNotFound += 1
                print(f"lost tag {timesNotFound} times")
            else:
                self.speeds = [0,0]
                print("lost it") #TODO this is bad
                timesNotFound = -1
                #return False
            self.printSpeeds()
            sleep(.1)
            count+=1
        self.speeds = [0,0]
        sleep(.5)
            
        if id2 == -1:            
            self.errorAccumulation = 0
            print("Locked on and ready to track")
            
            #Tracks down the tag
            while self.tracker.distanceToMarker > stopDistance or self.tracker.distanceToMarker == -1: #-1 means we lost the tag
                markerFound = self.tracker.findMarker(id1, cameras = 1) #Looks for the tag
                
                if self.tracker.distanceToMarker > stopDistance:
                    self.speeds = self.getSpeeds(self.baseSpeed-8, self.tracker.angleToMarker, 100, kp = .5, ki = .0001)
                    timesNotFound = 0
                    print(f"Tag is {self.tracker.distanceToMarker}cm away at {self.tracker.angleToMarker} degrees")
                    
                elif self.tracker.distanceToMarker == -1 and timesNotFound < 10:
                    timesNotFound += 1
                    print(f"lost tag {timesNotFound} times")
                    
                elif self.tracker.distanceToMarker == -1:
                    self.speeds = [0,0]
                    print("Lost tag")
                    return False #TODO this is bad
                
                self.printSpeeds()
                sleep(.1)
            
            #We scored!
            self.speeds = [0,0]
            print("In range of the tag!")
            return True
        else:
            #Gets the coords to the point that is 4m infront of the gate posts (get_coordinates expects distance in km)
            coords = self.gps.get_coordinates(self.tracker.distanceToMarker/100000.0+.004, self.tracker.angleToMarker)
            
            self.speeds = [self.baseSpeed, self.baseSpeed]
            sleep(5)
            
            #TODO: test this more after getting the new GPS
            '''
            #Rover hasn't been moving for a bit so moves to get correct bearing
            self.speeds = [-self.baseSpeed, -self.baseSpeed]
            self.printSpeeds()
            sleep(2)
            self.speeds = [0,0]
            self.printSpeeds()
            sleep(1)
            self.speeds = [self.baseSpeed, self.baseSpeed]
            self.printSpeeds()
            sleep(2)
            
            #Drives to the calculated location
            while self.gps.distance_to(coords[0], coords[1]) > .003: #TODO: might want to adjust distance here...
                bearingTo = self.gps.bearing_to(coords[0], coords[1])
                print(self.gps.distance_to(coords[0], coords[1]) )
                self.speeds = self.getSpeeds(self.baseSpeed, bearingTo, 100) #It will sleep for 100ms
                sleep(.1) #Sleeps for 100ms
                self.printSpeeds()
            '''
                        
        
         
    def backupManeuver(self):
        #backs up and turns to avoid running into the last detected sign. Also allows it to get a lock on heading
        self.speeds = [-60,-60]
        self.printSpeeds()
        sleep(2)
        self.speeds = [0,0]
        self.printSpeeds()
        sleep(2)
        self.speeds = [80,20]
        self.printSpeeds()
        sleep(4)