# Mission Control

This is all the code for either programs running on the mission control computers or the rover's onboard computer (Nvidia Jetson).

## udp_mc_arm

This is the arm remote control code for the linear actuator arm. Ideally, this should be updated. It was made with Qt5. It can be built by running "qmake" and then "make"
It communicates with the Arm arduino over ethernet. The arm device has the address 10.0.0.2:1002

## udp_mc_drill

***Add documentation here***

## udp_mc_drive

This is the drive remote control code from Soro4. It is programmed in Qt. The config file needs to know the ip of the computer it is running on (port doesn't really matter here) and the ip and port of the drive controller arduino. (10.0.0.1:1001)

## video_streamer

Documentation is inside the folder.
