import cv2 as cv
import cv2.aruco as aruco
import argparse
import configparser

# Read config file and set variables


def config():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.sections()
    config.read(args.filename)
    print(config['Config Values']['SWIFT_IP'])



def arFound(id, image, writeToFile):
    cv.cvtColor(src=image, code=cv.COLOR_RGB2GRAY, dest=image)
    index = -1

    # for i in range(40, 221, 60):


#def countValidARs(id1, id2, image, writeToFile):


#def findAR(id):


#def findARs(id1, id2):


#def trackAR(id):


#def trackARs(id1, id2):

config()