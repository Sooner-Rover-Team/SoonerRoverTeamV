# Autonomous Code
This folder contains all of the code needed for the autonomous program to run. We tied for 2nd in the 2022 autonomous course with this code when one of our wheels wasn't moving!

## Dependencies
Requires `opencv-contrib-python` to be installed
Run `pip3 install .` in this folder <br>

## Running
First, ensure that `main.py` drives to the desired ArUco markers <br>
To run the main autonomous program without awful debugging output, enter
`python3 main.py <camera_file> 2> /dev/null` <br>
* To get the camera file, enter `v4l2-ctl --list-devices` to find the desired camera's file. It will look like `/dev/video2` <br>
<br>
To view the rover's location and get coordinates, navigate to *`'rover's ip'`*`:5000` in your web browser

## Code Structure
### main.py
This is the program that gets run. This program allows the user to enter in GPS coordinates and then drives to the specified tags with -1 being given for a waypoint with no tag.

### Drive.py
The Drive class gives the user the ability to travel to a set of GPS locations while looking for a tag and then track either a tag or a gatepost after they've been seen.

### Location.py
API for using the GPS. Has methods that allows us to easily get the rover's heading and find how far the rover is from a set of GPS coordinates.

### UDPOut.py
Functions that allows the autonomous code to easily communicate to the MBed to control the wheels and LEDs.

### ARTracker.py
Class that gives the rover the ability to see ArUco markers and gets the rover's angle and distance from them. Also has the ability to utilize YOLO for the same purpose if the environment is properly setup.

### findFocalLength.py
Run this program directly to figure out the FOCAL_LENGTH parameters in config.ini

### gps
This folder contains the code needed to talk to the Swift GPS modules. I don't recommend going in here.

### runAutonomous.sh
Depricated. Can probably delete this but keeping it incase y'all ever go back to using three cameras


## Previous Code
Link to old, c++ autonomous code: https://github.com/eric-plus-plus/SoRo-19-20/tree/master/Autonomous
