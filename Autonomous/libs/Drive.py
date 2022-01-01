from threading import Thread
import configparser
import os
from time import sleep

from libs import UDPOut
from libs import Location
from libs import ARTracker

class Drive:
    
    def __init__(self, baseSpeed, cameras):
        self.baseSpeed = baseSpeed
        self.tracker = ARTracker.ARTracker(cameras)
        
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
        
        self.rightSpeed = 0.0
        self.leftSpeed = 0.0
        self.errorAccumulation = 0.0
        
        #starts the thread that sends wheel speeds
        self.running = True
        t = Thread(target=self.sendSpeed, name=('send wheel speeds'), args=())
        t.daemon = True
        t.start()
    
    #Every 100ms, send the current left and right wheel speeds to the mbeds
    def sendSpeed(self):
        while self.running:
            ls = int(self.leftSpeed)
            rs = int(self.rightSpeed)
            UDPOut.sendWheelSpeeds(self.mbedIP, self.mbedPort, ls,ls,ls, rs,rs,rs)
            sleep(.1)
    
    #time in milliseconds
    #error in degrees
    #Gets adjusted speeds based off of error and how long its been off (uses p and i)   
    def getSpeeds(self,speed, error, time):
        values = [0,0]

        #p and i constants if not doing a pivot turn
        kp = .3
        ki = .000001

        #p and i constants if doing a pivot turn
        if speed == 0:
            kp = .7
            ki = .0004

        #Updates the error accumulation
        self.errorAccumulation += error * time

        #Gets the adjusted speed values
        values[0] = speed - (error * kp + self.errorAccumulation * ki)
        values[1] = speed + (error * kp - self.errorAccumulation * ki)

        #Gets the maximum speed values depending if it is pivoting or not
        min = speed  - 30
        max = speed + 30
        if speed == 0:
            max += 30
            min -= 30
            
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
            
        return values
        
    #Cleaner way to print out the wheel speeds
    def printSpeeds(self):
        print("Left wheels: ", round(self.leftSpeed,1))
        print("Right wheels: ", round(self.rightSpeed,1))
    
    #Drives along a given list of GPS coordinates while looking for the given ar tags
    #Keep id2 at -1 if looking for one post, set id1 to -1 if you aren't looking for AR tags 
    def driveAlongCoordinates(self, locations, id1, id2=-1):
        #Starts the GPS
        self.gps.start_GPS_thread()
        print('Waiting for GPS connection...')
        #while self.gps.all_zero: 
        #    continue
        print('Connected to GPS')
        
        #backs up and turns to avoid running into the last detected sign. Also allows it to get a lock on heading
        self.leftSpeed = -60
        self.rightSpeed = -60
        sleep(2)
        self.leftSpeed = 0
        self.rightspeed = 0
        sleep(2)
        self.leftSpeed = 80
        self.rightSpeed = 20
        sleep(4)
        
        #navigates to each location
        for l in locations:
            self.errorAccumulation = 0
            while self.gps.distance_to(l[0], l[1]) > .002: #.002km
                bearingTo = self.gps.bearing_to(l[0], l[1])
                speeds = self.getSpeeds(self.baseSpeed, bearingTo, 100) #It will sleep for 100ms
                self.leftSpeed = speeds[1]
                self.rightSpeed = speeds[0]
                sleep(.1) #Sleeps for 100ms
                self.printSpeeds()
                if(id1 != -1 and self.tracker.findAR(id1, id2)):
                    self.gps.stop_GPS_thread()
                    print('Found Tag!')
                    self.leftSpeed = 0
                    self.rightSpeed = 0
                    return True
                    
        self.gps.stop_GPS_thread()
        print('Made it to location without seeing tag(s)')
        self.leftSpeed = 0
        self.rightSpeed = 0
        return False
                
    def trackARTag(self, id1, id2=-1):
        stopDistance = 250 #stops when 250cm from tags TODO make sure rover doesn't stop too far away with huddlys
        
                        
        
         
