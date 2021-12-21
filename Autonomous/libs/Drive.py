import UDPOut
import Location

class Drive:
    
    def init():
        config = configparser.ConfigParser()
        config.read(os.path.dirname(__file__) + '/../config.ini')
        
        mbedIP = str(config['CONFIG']['MBED_IP'])
        mbedPort = str(config['CONFIG']['MBED_PORT'])
        swiftIP = str(config['CONFIG']['SWIFT_IP'])
        swiftPort = str(config['CONFIG']['SWIFT_PORT'])
        
        gps = Location.Location('10.0.0.222','55556')\
        
        self.rightSpeed = 0
        self.leftSpeed = 0
        
    
        
        
