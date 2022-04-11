import sys
sys.path.append('../')
from math import cos, radians, degrees, sin, atan2, pi, sqrt, asin
import threading

# Class that computes functions related to location of Rover
# TODO: Make sure that the current GPS outputs coordinates
#       in the same format as the swift, and test out 
#       heading and see if that should be computed
#       somewhere outside of __parse
class LocationF9P:
    # To find the device path, run ls -l /dev/serial/by-id/usb-ublox_....(tab complete this)
    # and it will return where it's symlinked to, most likely /dev/ttyACM0
    # you could probably just use that /dev/serial path too
    def __init__(self, device_path="/dev/ttyACM0"):
        self.device_path = device_path
        self.device_open_file = None
        self.latitude = 0
        self.longitude = 0
        self.old_latitude = 0
        self.old_longitude = 0
        self.bearing = 0.0
        self.running = True

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
        if self.device_open_file == None:
            print("[Location-f9p.py] start_GPS_thread was called before opening the gps /dev/ entry - start_GPS will be called now")
            self.start_GPS()

        self.running = True
        t = threading.Thread(target=self.update_fields_loop, name=(
                'update GPS fields'), args=())
        t.daemon = True
        t.start()

    # Stops updating fields from GPS box
    def stop_GPS_thread(self):
        self.running = False

    def start_GPS(self):
        self.device_open_file = open(self.device_path)

    def update_fields_loop(self):
        while(self.running):
            line_read = self.device_open_file.readline()
            self.__parse(line_read)
        return

    # Parse NMEA messages read from the GPS.
    # The protocol is described on pdf page 24
    # of the integration manual (section 4.2.6)
    # https://cdn.sparkfun.com/assets/f/7/4/3/5/PM-15136.pdf
    def __parse(self, message_str):
        if isinstance(message_str, str):
            split = message_str.split(",")
            # look for lat/lon messages. We'll almost certainly get
            # GN messages (maybe only GN messages, but this theoretically accepts other talkers)
            if split[0].startswith("$") and split[0].endswith("GLL"):
                computed_checksum = 0
                for char in message_str:
                    if char == "*":
                        # marks the end of the portion to hash
                        break
                    elif char == "$":
                        # marks the beginning
                        computed_checksum = 0
                    else:
                        computed_checksum ^= ord(char)

                computed_checksum = format(computed_checksum, "X")
                message_checksum = (
                    message_str.split("*")[-1].replace("\n", "").replace("\r", "")
                )
                if computed_checksum != message_checksum:
                    print(
                        "`"
                        + format(computed_checksum, "X")
                        + "` did not match `"
                        + message_str.split("*")[-1]
                        + "`"
                    )
                    return

                self.old_latitude = self.latitude
                self.old_longitude = self.longitude

                # This is just a big pile of slicing up, the goal is to take:
                # $GNGLL,3511.93307,N,09721.15557,W,011244.00,A,D*64
                # and output the lat and lon.
                # It does this by:
                # - Parsing out the integer number of degrees (2 digits for lat, 3 digits for lon)
                # - Parsing out the minutes, and dividing them by 60, then adding them to the integer degrees
                # - Multiplying by -1 if the lat is in the south, or if the lon is in the west
                self.latitude = (int(split[1][0:2]) + float(split[1][2:]) / 60) * (
                    -1 if split[2] == "S" else 1
                )
                self.longitude = (int(split[3][0:3]) + float(split[3][3:]) / 60) * (
                    -1 if split[4] == "W" else 1
                )

                self.bearing = self.calc_bearing(self.old_latitude, self.old_longitude, self.latitude, self.longitude)
            elif not (
                message_str == "\n" or message_str == "\r\n" or message_str == ""
            ) and not message_str.startswith("$"):
                print(
                    "got weird message: " + message_str + " of len " + str(len(split))
                )

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
