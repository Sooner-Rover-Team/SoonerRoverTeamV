import cv2 as cv
import cv2.aruco as aruco
import configparser


# Read config file and set variables
def readConfig():
    config = configparser.ConfigParser()
    config.read('../config.ini')
    configVals = [0, 0, 0]
    configVals[0] = float(config['CONFIG']['DEGREES_PER_PIXEL'])
    configVals[1] = float(config['CONFIG']['FOCAL_LENGTH'])
    configVals[2] = float(config['CONFIG']['KNOWN_TAG_WIDTH'])
    return configVals

def arFound(id, image, writeToFile):
    cv.cvtColor(src=image, code=cv.COLOR_RGB2GRAY, dest=image)
    index = -1

#def countValidARs(id1, id2, image, writeToFile):


#def findAR(id):


#def findARs(id1, id2):


#def trackAR(id):


#def trackARs(id1, id2):

configVals = readConfig()
degreesPerPixel = configVals[0]
focalLength = configVals[1]
knownTagWidth = configVals[2]
