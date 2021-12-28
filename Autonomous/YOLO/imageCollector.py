import cv2 as cv
import os
import argparse
import time

parser = argparse.ArgumentParser(description='save images to file')

# add the arguments NEED TO WORK ON THESE
# camera
parser.add_argument('-cam', help='camera path', type=int, default=0)

# filepath
parser.add_argument('-file', help='File path where images will be stored', default='.')

# set frame capture rate to every 5 frames 
parser.add_argument('-captureRate', help='frame capture rate specifies collection frequency', type=int, default='5')

# set iteration to stop after 200 frames has been collected
parser.add_argument('-iterationLength', help='the duration of one iteration', type=int, default= 200)

# Execute the parse_args() method
args = parser.parse_args()

# Creates camera object
cam = cv.VideoCapture(args.cam)

# define counter 
counter = 0

# define the variable that counts number of frames collected
numFramesCollected = 0

while True:

    # reading from frame
    ret, frame = cam.read()

    # updates the window "preview" to show user captured frames 
    cv.imshow('preview', frame)

    # incrementing count 
    counter += 1

    # if count equals captureRate, save image 
    if counter == args.captureRate:

        # name filename based on timestamp 
        filename = args.file + '/' + str(time.time()) + '.jpg'
        cv.imwrite(filename, frame)

        # create .txt file with the same filename 
        # open("filename.txt", "w") -- accessmode "w" indicates python will write file and create 
        txtfilename = open(args.file + '/' + str(time.time()) + '.txt', "w")
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