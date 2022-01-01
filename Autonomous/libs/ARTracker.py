import cv2
import cv2.aruco as aruco
import numpy as np
import configparser
import os


class ARTracker:

    # Constructor
    def __init__(self, cameras, write=False):
        self.write=write
        self.distanceToTag = -1
        self.distanceToTag1 = 0
        self.distanceToTag2 = 0
        self.widthOfTag = 0.0
        self.widthOfTag1 = 0
        self.widthOfTag2 = 0
        self.centerXTag = 0
        self.angleToTag = -999.9

        #self.cameras = np.empty(3, dtype=str)
        self.cameras = cameras
        # Open the config file
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(os.path.dirname(__file__) + '/../config.ini')

        # Set variables from the config file
        self.degreesPerPixel = float(config['ARTRACKER']['DEGREES_PER_PIXEL'])
        self.focalLength = float(config['ARTRACKER']['FOCAL_LENGTH'])
        self.knownTagWidth = float(config['ARTRACKER']['KNOWN_TAG_WIDTH'])
        self.format = config['ARTRACKER']['FORMAT']
        self.frameWidth = int(config['ARTRACKER']['FRAME_WIDTH'])
        self.frameHeight = int(config['ARTRACKER']['FRAME_HEIGHT'])

        # Initialize video writer, fps is set 
        if self.write:
            self.videoWriter = cv2.VideoWriter("autonomous.avi", cv2.VideoWriter_fourcc(
                self.format[0], self.format[1], self.format[2], self.format[3]), 5, (self.frameWidth, self.frameHeight), False)
        # Set the ar tag dictionary
        self.tagDict = aruco.Dictionary_get(aruco.DICT_4X4_50)
        # Initialize cameras
        self.caps=[]
        for i in range(0, len(self.cameras)):
            self.caps.append(cv2.VideoCapture(self.cameras[i]))
            if not self.caps[i].isOpened():
                print(f"Camera ", i, " did not open!")
            self.caps[i].set(cv2.CAP_PROP_FRAME_WIDTH, self.frameWidth)
            self.caps[i].set(cv2.CAP_PROP_FRAME_HEIGHT, self.frameHeight)
            self.caps[i].set(cv2.CAP_PROP_BUFFERSIZE, 1) # greatly speeds up the program but the writer is a bit wack because of this
            self.caps[i].set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(self.format[0], self.format[1], self.format[2], self.format[3]))


    def arFound(self, id1, image, id2=-1):
        # converts to grayscale
        cv2.cvtColor(image, cv2.COLOR_RGB2GRAY, image)  
        
        index1 = -1
        index2 = -1
        bw = image #will hold the black and white image
        # tries converting to b&w using different different cutoffs to find the perfect one for the current lighting
        for i in range(40, 221, 60):
            bw = cv2.threshold(image,i,255, cv2.THRESH_BINARY)[1]
            (self.corners, self.markerIDs, self.rejected) = aruco.detectMarkers(bw, self.tagDict)   

            if not (self.markerIDs is None):
                
                if id2==-1:
                    index1 = -1 
                    # this just checks to make sure that it found the right tag
                    for i in range(len(self.markerIDs)):  
                        if self.markerIDs[i] == id1:
                            index1 = i 
                            break  
                
                    if index1 != -1:
                        print("Found the correct tag!")
                        if self.write:
                            self.videoWriter.write(bw)   #purely for debug   
                            cv2.waitKey(1)
                        break                    
                    
                    else:
                        print("Found a tag but was not the correct one") 
                
                else:
                    index1 = -1
                    index2 = -1
                    
                    if len(self.markerIDs) == 1:
                       print('Only found tag ', self.markerIDs[0])
                    else:
                        for i in range(len(self.markerIDs) - 1, -1,-1): #I trust the biggest tags the most
                            if self.markerIDs[i] == id1:
                                index1 = i 
                            elif self.markerIDs[i] == id2:
                                index2 = i
                    if index1 != -1 and index2 != -1:
                        print('Found both tags!')
                        if self.write:
                            self.videoWriter.write(bw)   #purely for debug   
                            cv2.waitKey(1)
                        break                        
                     
            if i == 220:  #did not find any AR tags with any b&w cutoff
                if self.write:
                    self.videoWriter.write(image) 
                    cv2.waitKey(1)
                self.distanceToTag = -1 
                self.angleToTag = -999 
                return False 
        
        if id2 == -1:
            self.widthOfTag = self.corners[index1][0][1][0] - self.corners[index1][0][0][0] 
            self.distanceToTag = (self.knownTagWidth * self.focalLength) / self.widthOfTag 
        
            self.centerXTag = (self.corners[index1][0][1][0] + self.corners[index1][0][0][0]) / 2 
            # takes the pixels from the tag to the center of the image and multiplies it by the degrees per pixel
            self.angleToTag = self.degreesPerPixel * (self.centerXTag - self.frameWidth/2)
        else:
            self.widthOfTag1 = self.corners[index1][0][1][0] - self.corners[index1][0][0][0] 
            self.widthOfTag2 = self.corners[index2][0][1][0] - self.corners[index2][0][0][0] 

            #distanceToAR = (knownWidthOfTag(20cm) * focalLengthOfCamera) / pixelWidthOfTag
            self.distanceToTag1 = (self.knownTagWidth * self.focalLength) / self.widthOfTag1
            self.distanceToTag2 = (self.knownTagWidth * self.focalLength) / self.widthOfTag2
            print(f"1: {self.distanceToTag1} \n2: {self.distanceToTag2}")
            self.distanceToTag = (self.distanceToTag1 + self.distanceToTag2) / 2
        
            self.centerXTag = (self.corners[index1][0][1][0] + self.corners[index2][0][0][0]) / 2
            #takes the pixels from the tag to the center of the image and multiplies it by the degrees per pixel
            self.angleToTag = self.degreesPerPixel * (self.centerXTag - self.frameWidth/2) 
    
        return True 

    #id1 is the tag you want to look for
    #specify id2 if you want to look for a gate
    #set write to true to write out images to disk
    #cameras=number of cameras to check. -1 for all of them
    def findAR(self, id1, id2=-1, cameras=-1):
        if cameras == -1:
            cameras=len(self.caps)
            
        for i in range(cameras):
            ret, frame = self.caps[i].read()
            if self.arFound(id1, frame, id2=id2): 
                return True

        return False
