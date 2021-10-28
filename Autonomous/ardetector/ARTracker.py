import cv2 as cv
import cv2.aruco as aruco
import numpy as np
import configparser


class ARTracker:

    # Constructor
    def __init__(self, cameras):
        self.cameras = np.empty(3, dtype=str)
        self.cameras = cameras
        # Open the config file
        config = configparser.ConfigParser()
        config.read('../config.ini')

        # Set variables from the config file
        self.degreesPerPixel = float(config['ARTRACKER']['DEGREES_PER_PIXEL'])
        self.focalLength = float(config['ARTRACKER']['FOCAL_LENGTH'])
        self.knownTagWidth = float(config['ARTRACKER']['KNOWN_TAG_WIDTH'])
        self.format = config['ARTRACKER']['FORMAT']
        self.frameWidth = float(config['ARTRACKER']['FRAME_WIDTH'])
        self.frameHeight = float(config['ARTRACKER']['FRAME_HEIGHT'])
        
        # Initialize video writer
        self.videoWriter = cv.VideoWriter("autonomous.avi", cv.VideoWriter_fourcc(
            self.format[0], self.format[1], self.format[2], self.format[3]), 5, (1920, 1080), False)
        # Set the ar tag dictionary
        self.tagDict = aruco.DICT_4X4_50
        # Initialize cameras
        self.caps = np.empty(3, dtype=cv.VideoCapture)
        for i in range(0, self.cameras.size):
            self.caps[i] = cv.VideoCapture(self.cameras[i])
            if not self.caps[i].isOpened():
                print(f"Camera  i  did not open!")
            self.caps[i].set(cv.CAP_PROP_FRAME_WIDTH, self.frameWidth)
            self.caps[i].set(cv.CAP_PROP_FRAME_HEIGHT, self.frameHeight)
            self.caps[i].set(cv.CAP_PROP_BUFFERSIZE, 1) # greatly speeds up the program but the writer is a bit wack because of this
            self.caps[i].set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(self.format[0], self.format[1], self.format[2], self.format[3]))

    def arFound(self, id, image, writeToFile):
        # converts to grayscale
        cv.cvtColor(image, image, cv.COLOR_RGB2GRAY)  
        
        index = -1  
        # tries converting to b&w using different different cutoffs to find the perfect one for the current lighting
        for i in range(40, 221, 60):
            # FIXME corners = [], MarkerIDs = [], rejects = []
            # detects all of the tags in the current b&w cutoff
            aruco.detectMarkers((image > i), self.tagDict, corners, MarkerIDs, rejects)   
        
            if MarkerIDs.length > 0:
             
                index = -1 
                # this just checks to make sure that it found the right tag. Probably should move this into the b&w block
                for i in range(MarkerIDs.length):  
                    if MarkerIDs[i] == id:
                        index = i 
                        break  
            
                if index != -1:
                    print("Found the correct tag!")
                    if writeToFile:
                        mFrame = image > i   #purely for debug
                        self.videoWriter.write(mFrame)   #purely for debug   
                    break                    
	            
                else:
                    print("Found a tag but was not the correct one") 
             

            if i == 220:  #did not find any AR tags with any b&w cutoff
             
                if writeToFile:
                    self.videoWriter.write(image) 
                distanceToAR = -1 
                angleToAR = 0 
                return False 
             
         
        widthOfTag = corners[index][1].x - corners[index][0].x 
        distanceToAR = (self.knownTagWidth * self.focalLength) / widthOfTag 
    
        centerXTag = (corners[index][1].x + corners[index][0].x) / 2 
        # takes the pixels from the tag to the center of the image and multiplies it by the degrees per pixel
        angleToAR = self.degreesPerPixel * (centerXTag - 960)   
    
        return True 
         


    # def countValidARs(self, id1, id2, image, writeToFile):

    # def findAR(self, id):

    # def findARs(self, id1, id2):

    # def trackAR(self, id):

    # def trackARs(self, id1, id2):


cams = np.empty(3, dtype=str)
cams[0] = '2.3'
cams[1] = '2.4'
cams[2] = '2.2'
tracker = ARTracker(cams)
