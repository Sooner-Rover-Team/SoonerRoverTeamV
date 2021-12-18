import cv2
import cv2.aruco as aruco
import numpy as np
import configparser

class ARTracker:

    # Constructor
    def __init__(self, cameras):
        self.distanceToAR = 0
        self.distanceToAR1 = 0
        self.distanceToAR2 = 0
        self.widthOfTag = 0.0
        self.widthOfTag1 = 0
        self.widthOfTag2 = 0
        self.centerXTag = 0
        self.angleToAR = 0.0

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
        self.videoWriter = cv2.VideoWriter("autonomous.avi", cv2.VideoWriter_fourcc(
            self.format[0], self.format[1], self.format[2], self.format[3]), 5, (1920, 1080), False)
        # Set the ar tag dictionary
        self.tagDict = aruco.DICT_4X4_50
        # Initialize cameras
        self.caps = np.empty(3, dtype=cv2.VideoCapture)
        for i in range(0, self.cameras.size):
            self.caps[i] = cv2.VideoCapture(self.cameras[i])
            if not self.caps[i].isOpened():
                print(f"Camera  i  did not open!")
            self.caps[i].set(cv2.CAP_PROP_FRAME_WIDTH, self.frameWidth)
            self.caps[i].set(cv2.CAP_PROP_FRAME_HEIGHT, self.frameHeight)
            self.caps[i].set(cv2.CAP_PROP_BUFFERSIZE, 1) # greatly speeds up the program but the writer is a bit wack because of this
            self.caps[i].set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(self.format[0], self.format[1], self.format[2], self.format[3]))


    def arFound(self, id, image, writeToFile):
        # converts to grayscale
        cv2.cvtColor(image, cv2.COLOR_RGB2GRAY, image)  
        
        index = -1  
        # tries converting to b&w using different different cutoffs to find the perfect one for the current lighting
        for i in range(40, 221, 60):
            (self.corners, self.markerIDs, self.rejected) = aruco.detectMarkers((image > i), self.tagDict)   
        
            if self.markerIDs.length > 0:
             
                index = -1 
                # this just checks to make sure that it found the right tag. Probably should move this into the b&w block
                for i in range(self.markerIDs.length):  
                    if self.markerIDs[i] == id:
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
                self.distanceToAR = -1 
                self.angleToAR = 0 
                return False 
             
        self.widthOfTag = self.corners[index][1].x - self.corners[index][0].x 
        self.distanceToAR = (self.knownTagWidth * self.focalLength) / self.widthOfTag 
    
        self.centerXTag = (self.corners[index][1].x + self.corners[index][0].x) / 2 
        # takes the pixels from the tag to the center of the image and multiplies it by the degrees per pixel
        self.angleToAR = self.degreesPerPixel * (self.centerXTag - 960)   
    
        return True 
         

    def countValidARs(self, id1, id2, image, writeToFile):
        cv2.cvtColor(image, cv2.COLOR_RGB2GRAY, image) # converts to grayscale
    
        # tries converting to b&w using different different cutoffs to find the perfect one for the ar tag
        for i in range(40, 221, 60):
            (self.corners, self.markerIDs, self.rejected) = aruco.detectMarkers((image > i), self.tagDict)
            if self.markerIDs.length > 0:

                if self.markerIDs.length == 1:
                    print("Just found one post")

                else:
                    if writeToFile:
                        mFrame = image > i # purely for debug
                        self.videoWriter.write(mFrame) # purely for debug
                    break
        
            if i == 220: # did not ever find two ars. TODO add something for if it finds one tag
                if writeToFile:
                    self.videoWriter.write(image)
                self.distanceToAR = -1
                self.angleToAR = 0
                return 0

        index1 = -1
        index2 = -1
        for i in range(self.markerIDs.length): # this just checks to make sure that it found the right tags
            if self.markerIDs[i] == id1 or self.markerIDs[i] == id2:
                if self.markerIDs[i] == id1:
                    index1 = i
                else:
                    index2=i
            
                if index1 != -1 and index2 != -1:
                    break

        if index1 == -1 or index2 == -1: 
            self.distanceToAR = -1
            self.angleToAR = 0
            print(f"index1: {index1} \nindex2: {index2}")
            if index1 != -1 or index2 != -1:
                return 1
            return 0 # no correct ar tags found
        else:
            self.widthOfTag1 = self.corners[index1][1].x - self.corners[index1][0].x
            self.widthOfTag2 = self.corners[index2][1].x - self.corners[index2][0].x

            #distanceToAR = (knownWidthOfTag(20cm) * focalLengthOfCamera) / pixelWidthOfTag
            self.distanceToAR1 = (self.knownTagWidth * self.focalLength) / self.widthOfTag1
            self.distanceToAR2 = (self.knownTagWidth * self.focalLength) / self.widthOfTag2
            print(f"1: {self.distanceToAR1} \n2: {self.distanceToAR2}")
            print(f"focal: {self.focalLength} \nwidth: {self.widthOfTag}")
            self.distanceToAR = (self.distanceToAR1 + self.distanceToAR2) / 2
            print(self.distanceToAR)
        
            self.centerXTag = (self.corners[index1][1].x + self.corners[index2][0].x) / 2
            self.angleToAR = self.degreesPerPixel * (self.centerXTag - 960) #takes the pixels from the tag to the center of the image and multiplies it by the degrees per pixel
        
            return 2


    # def findAR(self, id):

    # def findARs(self, id1, id2):

    # def trackAR(self, id):

    # def trackARs(self, id1, id2):


cams = np.empty(3, dtype=str)
cams[0] = '2.3'
cams[1] = '2.4'
cams[2] = '2.2'
tracker = ARTracker(cams)
