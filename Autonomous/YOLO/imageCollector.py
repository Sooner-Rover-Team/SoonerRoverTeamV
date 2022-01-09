import cv2 as cv
import cv2
import numpy as np
import os
import argparse
import time
import sys

# Set the ar tag dictionary
tagDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)

# creates and initializes the parser (allows custom arguments)
parser = argparse.ArgumentParser(description='save images to file')

parser.add_argument('-cam', help='camera path', type=int, default=0)
parser.add_argument('-file', help='File path where images will be stored', default='.')
parser.add_argument('-captureRate', help='frame capture rate specifies collection frequency', type=int, default='10') # Changed default from 5 to 10
parser.add_argument('-iterationLength', help='the duration of one iteration', type=int, default= 200)
parser.add_argument('-arMode', help='arMode identifies the arTags in captured frames, argument is "run"', action='count', default=0)
parser.add_argument('-tagIDs', nargs='+', type=int, default=[0], help='Array of tag ids') 
# Parse the arguments
args = parser.parse_args()

# Creates camera object 
cam = cv.VideoCapture(args.cam)
if not cam.isOpened():
    print("!!!!!CAMERA DID NOT OPEN!!!!!")
    sys.exit()

# define counter (this counter determines the rate at which frames are collected, ie every 5 frames)
counter = 0

# define the variable that counts number of frames collected (determines the iteration length of collection, ie stop at 200)
numFramesCollected = 0

while True:
    fileTime = str(time.time_ns())
    # if the user specifies to run code through arMode 
    if args.arMode: 
        
        # reading from frame 
        ret, frame = cam.read() 

        # updates the window "preview" to show user captured frames 
        cv.imshow('preview', frame) 

        # incrementing count 
        counter += 1 

        # if count equals captureRate, save image  
        if counter == args.captureRate:  

            # converts image to grayscale 
            bwFrame = cv.cvtColor(frame, cv.COLOR_RGB2GRAY, frame) 

            # name filename based on timestamp and add it to specified filepath 
            filename = args.file + '/' + fileTime + '.jpg'

            for i in range(40, 221, 60): 
                bwFrame = cv.threshold(frame, i, 255, cv.THRESH_BINARY)[1]

                # corners: x,y coordinates of our detected markers
                # markerIDs: identifers of the marker (the ID encoded in the marker itself)
                # rejected: potential markers detected but rejected bc code inside marker couldn't be parsed 
                # bwFrame: frame converted to grayscale 
                # tagDict: tag dictionary we previously set up 
                (corners, markerIDs, rejected) = cv2.aruco.detectMarkers(bwFrame, tagDict)
                print(markerIDs)
                # determining the height and width of the frame (NOT THE TAG) 
                height, width = bwFrame.shape[0], bwFrame.shape[1]
                
                # if any markerIDs were detected in the frame 
                # basically if markerIDs > 0 
                if not (markerIDs is None) : 
                    cv.imwrite(filename, frame)
                    #markerIDs = markerIDs.flatten()
                    for i in range(0, len(markerIDs)):
                        print(i)
                        if markerIDs[i][0] <= 7:
                            # X and Y coordinates: 
                            # determined by finding the midpoint of x and y (i.e. ((x1 + x2)/2)) and dividing by image width or height
                            # Notes: X_CENTER_NORM = X_CENTER_ABS/IMAGE_WIDTH
                            # Notes: Y_CENTER_NORM = Y_CENTER_ABS/IMAGE_HEIGHT
                            xTag = ((corners[i][0][1][0] + corners[i][0][0][0] + corners[i][0][2][0] + corners[i][0][3][0]) / 4 ) / width
                            yTag = ((corners[i][0][1][1] + corners[i][0][2][1]) / 2 ) / height

                            # Width and Height of Tag: 
                            # Notes: WIDTH_NORM = WIDTH_OF_LABEL_ABS/IMAGE_WIDTH
                            # Notes: HEIGHT_NORM = HEIGHT_OF_LABEL_ABS/IMAGE_HEIGHT
                            widthOfTag = (((corners[i][0][1][0] - corners[i][0][0][0]) + (corners[i][0][2][0] - corners[i][0][3][0])) / 2)  / width
                            heightOfTag = (corners[i][0][2][1] - corners[i][0][1][1]) / height

                            # create .txt file with the same filename 
                            # open("filename.txt", "w") -- accessmode "w" indicates python will write and create the new file 
                            txtfilename = open(args.file + '/' + fileTime + '.txt', "a") 
                            # write in the txt file: 0  X_CENTER_NORM  Y_CENTER_NORM  WIDTH_NORM  HEIGHT_NORM 
                            txtfilename.write("0 " + str(xTag) + " " + str(yTag)  + " " + str(widthOfTag) + " " + str(heightOfTag) + "\n")
                            txtfilename.close()

                # AR Tag is not found 
                else: 
                    # create .txt file with the same filename 
                    print("sucks to suck")
                    #pass
                    # open("filename.txt", "w") -- accessmode "w" indicates python will write and create the new file 
                    # txtfilename = open(args.file + '/' + fileTime + '.txt', "w")
                    # file will be empty if AR Tag is not found 
                    # txtfilename.write("")
                    # txtfilename.close

            # increment the number of frames collected 
            numFramesCollected += 1

            #reset counter
            counter = 0

        # quit if user presses 'q' or when 200 frames has been collected 
        if cv.waitKey(1) == ord('q') or numFramesCollected == args.iterationLength:
            break



    # if the user chooses not to run code through arMode 
    else: 
        # reading from frame
        ret, frame = cam.read()

        # updates the window "preview" to show user captured frames 
        cv.imshow('preview', frame)

        # incrementing count 
        counter += 1

        # if count equals captureRate, save image 
        if counter == args.captureRate:

            # name filename based on timestamp and add it to specified filepath 
            filename = args.file + '/' + fileTime + '.jpg'
            cv.imwrite(filename, frame)

            # create .txt file with the same filename 
            # open("filename.txt", "w") -- accessmode "w" indicates python will write and create the new file 
            txtfilename = open(args.file + '/' + fileTime + '.txt', "w")
            # file will be empty if code is not run through arMode  
            txtfilename.write("")
            txtfilename.close

            # increment the number of frames collected 
            numFramesCollected += 1

            #reset counter
            counter = 0

        # quit if user presses 'q' or when 200 frames has been collected 
        if cv.waitKey(1) == ord('q') or numFramesCollected == args.iterationLength:
            break

cam.release()
cv.destroyAllWindows()
