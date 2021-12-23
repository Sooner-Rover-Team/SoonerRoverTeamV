import cv2
import os
import argparse
import time

my_parser = argparse.ArgumentParser(description='save images to file')

# add the arguments NEED TO WORK ON THESE
# camera
my_parser.add_argument('cam', help='camera path', type=int, default=0)

# filepath
my_parser.add_argument('filepath', help='File path where images will be stored')

# Execute the parse_args() method
args = my_parser.parse_args()

cam = cv2.VideoCapture(args.cam)

# camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:

    ret, frame = cam.read()
    cv2.imshow('preview', frame)

    filename = filepath + args.file + '/' + str(time.time()) + '.jpg'
    cv2.imwrite(filename, frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindow()