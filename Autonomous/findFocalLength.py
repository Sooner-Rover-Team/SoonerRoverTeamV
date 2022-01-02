#!/usr/bin/python3

#This programs returns the camera focal length assuming tag is tag 0, 20cm wide and 100cm away
import cv2
import cv2.aruco as aruco
import numpy as np
import os
import configparser

#opens the camera
cam = cv2.VideoCapture('/dev/video0')
if not cam.isOpened():
    print("Camera not connected")
    exit(-1)

#sets up the config stuff
config = configparser.ConfigParser(allow_no_value=True)
config.read(os.path.dirname(__file__) + '/config.ini')

#sets the resolution and 4cc
format = config['ARTRACKER']['FORMAT']
cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(format[0], format[1], format[2], format[3]))
cam.set(cv2.CAP_PROP_FRAME_WIDTH, int(config['ARTRACKER']['FRAME_WIDTH']))
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, int(config['ARTRACKER']['FRAME_HEIGHT']))

tagDict = aruco.Dictionary_get(aruco.DICT_4X4_50)

while True:
    try:
        #takes image and detects markers
        ret, image = cam.read()
        corners, markerIDs, rejected = aruco.detectMarkers(image, tagDict)
        
        tagWidth = 0
        if not markerIDs is None and markerIDs[0] == 0: #looking for tag 0
            tagWidth = corners[0][0][1][0] - corners[0][0][0][0] 
            focalLength = (tagWidth * 100) / 20 #Assumes tag is 20cm wide and 100cm away
            print("Focal length: ", focalLength)
        else:
            print("Nothing found")
    
    except KeyboardInterrupt:
        break
    except:
        pass #When running multiple times in a row, must cycle through a few times
       
cam.release() #releases the camera
