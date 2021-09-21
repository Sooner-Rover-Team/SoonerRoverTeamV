import cv2 as cv
import cv2.aruco as aruco
import argparse

# Read config file and set variables
def config():
    configFile = open("../config.txt")
    configData = configFile.readlines()
    #for line in configData:


def arFound(id, image, writeToFile):
    cv.cvtColor(src=image, code=cv.COLOR_RGB2GRAY, dest=image)
    index = -1

    #for i in range(40, 221, 60):

def countValidARs(id1, id2, image, writeToFile):


def findAR(id):


def findARs(id1, id2):


def trackAR(id):


def trackARs(id1, id2):
