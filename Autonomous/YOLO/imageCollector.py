import cv2 as cv
import cv2
import numpy as np
import os
import argparse
import time

# Set the ar tag dictionary
tagDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)

# creates and initializes the parser (allows custom arguments)
parser = argparse.ArgumentParser(description='save images to file')

# add the arguments
# camera
parser.add_argument('-cam', help='camera path', type=int, default=0)

# filepath
parser.add_argument('-file', help='File path where images will be stored', default='.')

# set frame capture rate to every 5 frames
parser.add_argument('-captureRate', help='frame capture rate specifies collection frequency', type=int, default='5')

# set iteration to stop after 200 frames has been collected
parser.add_argument('-iterationLength', help='the duration of one iteration', type=int, default= 200)

# arMode - user decides through command prompt if they want code to run through arMode 
parser.add_argument('-arMode', help='arMode identifies the arTags in captured frames, argument is "run"', type=str, default='.')

# Execute the parse_args() method (parse the argument) 
args = parser.parse_args()

# Creates camera object 
cam = cv.VideoCapture(args.cam)

# define counter 
counter = 0

# define the variable that counts number of frames collected 
numFramesCollected = 0

while True:

    # if the user specifies to run code through arMode 
    if args.arMode == "run": 

        # testing block 
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
            filename = args.file + '/' + str(time.time()) + '.jpg'
            # assigning the converted grayscale image to the filename
            cv.imwrite(filename, bwFrame)

            # Add note 
            for i in range(40, 221, 60): 
                bwFrame = cv.threshold(frame, i, 255, cv.THRESH_BINARY)[1]
                # corners: x,y coordinates of our detected markers
                # markerIDs: identifers of the marker (the ID encoded in the marker itself)
                # rejected: potential markers detected but rejected bc code inside marker couldn't be parsed 
                # bwFrame: frame converted to grayscale 
                # tagDict: tag dictionary we previously set up 
                (corners, markerIDs, rejected) = cv2.aruco.detectMarkers(bwFrame, tagDict)

                # determining the height and width of the frame (NOT THE TAG) 
                height, width = bwFrame.shape[0], bwFrame.shape[1]
                # print("h" + str(h) + ", w" + str(w))       #debugging print
                
                # if any markerIDs were detected in the frame 
                # basically if markerIDs > 0 
                if not (markerIDs is None) : 
                    
                    # X and Y coordinates: 
                    # determined by finding the midpoint of x and y (i.e. ((x1 + x2)/2)) and dividing by image width or height
                    # Notes: X_CENTER_NORM = X_CENTER_ABS/IMAGE_WIDTH
                    # Notes: Y_CENTER_NORM = Y_CENTER_ABS/IMAGE_HEIGHT
                    xTag = ((corners[0][0][1][0] + corners[0][0][0][0]) / 2 ) / width
                    yTag = ((corners[0][0][1][0] + corners[0][0][0][0]) / 2 ) / height

                    # Width and Height of Tag: 
                    # Notes: WIDTH_NORM = WIDTH_OF_LABEL_ABS/IMAGE_WIDTH
                    # Notes: HEIGHT_NORM = HEIGHT_OF_LABEL_ABS/IMAGE_HEIGHT
                    widthOfTag = (corners[0][0][1][0] - corners[0][0][0][0]) / width
                    heightOfTag = (corners[0][0][1][0] - corners[0][0][0][0]) / height

                    # converting centerXTag and centerYTag from numpy long to str (if not, will produce error)
                    print("(" + str(xTag) + ", " + str(yTag) + ")")

                    # create .txt file with the same filename 
                    # open("filename.txt", "w") -- accessmode "w" indicates python will write and create the new file 
                    txtfilename = open(args.file + '/' + str(time.time()) + '.txt', "w") 
                    # write in the txt file: 0  X_CENTER_NORM  Y_CENTER_NORM  WIDTH_NORM  HEIGHT_NORM 
                    # we are writing in the txt file since there was an AR Tag found 
                    txtfilename.write("0 " + str(xTag) + " " + str(yTag)  + " " + str(widthOfTag) + " " + str(heightOfTag))
                    txtfilename.close()

                # AR Tag is not found 
                else: 
                    # create .txt file with the same filename 
                    # open("filename.txt", "w") -- accessmode "w" indicates python will write and create the new file 
                    txtfilename = open(args.file + '/' + str(time.time()) + '.txt', "w")
                    # file will be empty if AR Tag is not found 
                    txtfilename.write("")
                    txtfilename.close

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
            filename = args.file + '/' + str(time.time()) + '.jpg'
            cv.imwrite(filename, frame)

            # create .txt file with the same filename 
            # open("filename.txt", "w") -- accessmode "w" indicates python will write and create the new file 
            txtfilename = open(args.file + '/' + str(time.time()) + '.txt', "w")
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
cv.destroyAllWindow()