from threading import Thread

import UDPOut
import Location

class Drive:
    
    def init(baseSpeed):
        self.baseSpeed = baseSpeed
        
        config = configparser.ConfigParser()
        config.read(os.path.dirname(__file__) + '/../config.ini')
        
        mbedIP = str(config['CONFIG']['MBED_IP'])
        mbedPort = str(config['CONFIG']['MBED_PORT'])
        swiftIP = str(config['CONFIG']['SWIFT_IP'])
        swiftPort = str(config['CONFIG']['SWIFT_PORT'])
        
        gps = Location.Location('10.0.0.222','55556')
        
        self.rightSpeed = 0
        self.leftSpeed = 0
        self.errorAccumulation = 0
        
        self.running = True
        t = Thread(target=self.sendSpeed, name=('send wheel speeds'), args=())
        t.daemon = True
        t.start()
        
    def sendSpeed():
        while running:
            UDPOut.sendWheelSpeeds(self.mbedIP, self.mbedPort, self.leftSpeed, self.leftSpeed, self.leftSpeed, self.rightSpeed, self.rightSpeed, self.rightSpeed)
            sleep(.1)
        
    def getSpeeds(speed, error, time):
        values = [0,0]

        kp = .3
        ki = .000001

        if speed == 0:
            kp = .7
            ki = .0004

        errorAccumulation += error * time

        values[0] = baseSpeed - (error * kp + errorAccumulation * ki)
        values[1] = baseSpeed + (error * kp - errorAccumulation * ki)

        min = baseSpeed  + 30
        max = baseSpeed - 30
        if baseSpeed == 0:
            max += 30
            min -= 30
            
        if values[0] > max:
            values[0] = max
        elif values[0] < min:
            values[0] = min
            
        if values[1] > max:
            values[1] = max
        elif values[1] < min:
            values[1] = min
       
        if values[0] <= 0 and values[0] > -10:
            values[0] = -10
        elif values[0] > 0 and values[0] < 10:
            values[0] = 10
        
        if values[1] <= 0 and values[1] > -10:
            values[1] = -10
        elif values[1] > 0 and values[1] < 10:
            values[1] = 10
        
        return values
        
         
