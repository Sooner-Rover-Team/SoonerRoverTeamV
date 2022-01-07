import cv2
import cv2.aruco as aruco
import numpy as np
import configparser
import os


class ARTracker:

    # Constructor
    def __init__(self, cameras, write=False):
        self.write=write
        self.distanceToMarker = -1
        self.angleToMarker = -999.9
        self.index1 = -1
        self.index2 = -1

        #self.cameras = np.empty(3, dtype=str)
        self.cameras = cameras
        # Open the config file
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(os.path.dirname(__file__) + '/../config.ini')

        # Set variables from the config file
        self.degreesPerPixel = float(config['ARTRACKER']['DEGREES_PER_PIXEL'])
        self.vDegreesPerPixel = float(config['ARTRACKER']['VDEGREES_PER_PIXEL'])
        self.focalLength = float(config['ARTRACKER']['FOCAL_LENGTH'])
        self.focalLength30H = float(config['ARTRACKER']['FOCAL_LENGTH30H'])
        self.focalLength30V = float(config['ARTRACKER']['FOCAL_LENGTH30V'])
        self.knownMarkerWidth = float(config['ARTRACKER']['KNOWN_TAG_WIDTH'])
        self.format = config['ARTRACKER']['FORMAT']
        self.frameWidth = int(config['ARTRACKER']['FRAME_WIDTH'])
        self.frameHeight = int(config['ARTRACKER']['FRAME_HEIGHT'])

        # Initialize video writer, fps is set 
        if self.write:
            self.videoWriter = cv2.VideoWriter("autonomous.avi", cv2.VideoWriter_fourcc(
                self.format[0], self.format[1], self.format[2], self.format[3]), 5, (self.frameWidth, self.frameHeight), False)
        # Set the ar marker dictionary
        self.markerDict = aruco.Dictionary_get(aruco.DICT_4X4_50)
        # Initialize cameras
        self.caps=[]
        for i in range(0, len(self.cameras)):
            self.caps.append(cv2.VideoCapture(self.cameras[i]))
            if not self.caps[i].isOpened():
                print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!Camera ", i, " did not open!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.caps[i].set(cv2.CAP_PROP_FRAME_WIDTH, self.frameWidth)
            self.caps[i].set(cv2.CAP_PROP_FRAME_HEIGHT, self.frameHeight)
            self.caps[i].set(cv2.CAP_PROP_BUFFERSIZE, 1) # greatly speeds up the program but the writer is a bit wack because of this
            self.caps[i].set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(self.format[0], self.format[1], self.format[2], self.format[3]))
    
    #id1 is the main ar tag to track, id2 is if you're looking at a gatepost, image is the image to analyze
    def markerFound(self, id1, image, id2=-1):
        # converts to grayscale
        cv2.cvtColor(image, cv2.COLOR_RGB2GRAY, image)  
        
        self.index1 = -1
        self.index2 = -1
        bw = image #will hold the black and white image
        # tries converting to b&w using different different cutoffs to find the perfect one for the current lighting
        for i in range(40, 221, 60):
            bw = cv2.threshold(image,i,255, cv2.THRESH_BINARY)[1]
            (self.corners, self.markerIDs, self.rejected) = aruco.detectMarkers(bw, self.markerDict)   

            if not (self.markerIDs is None):
                
                if id2==-1: #single post
                    self.index1 = -1 
                    # this just checks to make sure that it found the right marker
                    for i in range(len(self.markerIDs)):  
                        if self.markerIDs[i] == id1:
                            self.index1 = i 
                            break  
                
                    if self.index1 != -1:
                        print("Found the correct marker!")
                        if self.write:
                            self.videoWriter.write(bw)   #purely for debug   
                            cv2.waitKey(1)
                        break                    
                    
                    else:
                        print("Found a marker but was not the correct one") 
                
                else: #gate post
                    self.index1 = -1
                    self.index2 = -1
                    if len(self.markerIDs) == 1: 
                       print('Only found marker ', self.markerIDs[0])
                    else:
                        for j in range(len(self.markerIDs) - 1, -1,-1): #I trust the biggest markers the most
                            if self.markerIDs[j][0] == id1:
                                self.index1 = j 
                            elif self.markerIDs[j][0] == id2:
                                self.index2 = j
                    if self.index1 != -1 and self.index2 != -1:
                        print('Found both markers!')
                        if self.write:
                            self.videoWriter.write(bw)   #purely for debug   
                            cv2.waitKey(1)
                        break                        
                     
            if i == 220:  #did not find any AR markers with any b&w cutoff
                if self.write:
                    self.videoWriter.write(image) 
                    cv2.waitKey(1)
                self.distanceToMarker = -1 
                self.angleToMarker = -999 
                return False 
        
        if id2 == -1:
            centerXMarker = (self.corners[self.index1][0][0][0] + self.corners[self.index1][0][1][0] + \
                self.corners[self.index1][0][2][0] + self.corners[self.index1][0][3][0]) / 4
            # takes the pixels from the marker to the center of the image and multiplies it by the degrees per pixel
            self.angleToMarker = self.degreesPerPixel * (centerXMarker - self.frameWidth/2)
        
            '''
            distanceToAR = (knownWidthOfMarker(20cm) * focalLengthOfCamera) / pixelWidthOfMarker
            focalLength = focal length at 0 degrees horizontal and 0 degrees vertical
            focalLength30H = focal length at 30 degreees horizontal and 0 degrees vertical
            focalLength30V = focal length at 30 degrees vertical and 0 degrees horizontal
            realFocalLength of camera = focalLength 
                                        + (horizontal angle to marker/30) * (focalLength30H - focalLength)
                                        + (vertical angle to marker / 30) * (focalLength30V - focalLength)
            If focalLength30H and focalLength30V both equal focalLength then realFocalLength = focalLength which is good for non huddly cameras
            Please note that the realFocalLength calculation is an approximations that could be much better if anyone wants to try to come up with something better
            '''
            hAngleToMarker = abs(self.angleToMarker)
            centerYMarker = (self.corners[self.index1][0][0][1] + self.corners[self.index1][0][1][1] + \
                self.corners[self.index1][0][2][1] + self.corners[self.index1][0][3][1]) / 4
            vAngleToMarker = abs(self.vDegreesPerPixel * (centerYMarker - self.frameHeight/2))
            realFocalLength = self.focalLength + (hAngleToMarker/30) * (self.focalLength30H - self.focalLength) + \
                (vAngleToMarker/30) * (self.focalLength30V - self.focalLength)
            widthOfMarker = ((self.corners[self.index1][0][1][0] - self.corners[self.index1][0][0][0]) + \
                (self.corners[self.index1][0][2][0] - self.corners[self.index1][0][3][0])) / 2
            self.distanceToMarker = (self.knownMarkerWidth * realFocalLength) / widthOfMarker 
            
        else:
            centerXMarker1 = (self.corners[self.index1][0][0][0] + self.corners[self.index1][0][1][0] + \
                self.corners[self.index1][0][2][0] + self.corners[self.index1][0][3][0]) / 4
            centerXMarker2 = (self.corners[self.index2][0][0][0] + self.corners[self.index2][0][1][0] + \
                self.corners[self.index2][0][2][0] + self.corners[self.index2][0][3][0]) / 4
            self.angleToMarker = self.degreesPerPixel * ((centerXMarker1 + centerXMarker2)/2 - self.frameWidth/2) 
        
            hAngleToMarker1 = abs(self.vDegreesPerPixel * (centerXMarker1 - self.frameWidth/2))
            hAngleToMarker2 = abs(self.vDegreesPerPixel * (centerXMarker2 - self.frameWidth/2))
            centerYMarker1 = (self.corners[self.index1][0][0][1] + self.corners[self.index1][0][1][1] + \
                self.corners[self.index1][0][2][1] + self.corners[self.index1][0][3][1]) / 4
            centerYMarker2 = (self.corners[self.index2][0][0][1] + self.corners[self.index2][0][1][1] + \
                self.corners[self.index2][0][2][1] + self.corners[self.index2][0][3][1]) / 4
            vAngleToMarker1 = abs(self.vDegreesPerPixel * (centerYMarker1 - self.frameHeight/2))
            vAngleToMarker2 = abs(self.vDegreesPerPixel * (centerYMarker2 - self.frameHeight/2))
            realFocalLength1 = self.focalLength + (hAngleToMarker1/30) * (self.focalLength30H - self.focalLength) + \
                (vAngleToMarker1/30) * (self.focalLength30V - self.focalLength)
            realFocalLength2 = self.focalLength + (hAngleToMarker2/30) * (self.focalLength30H - self.focalLength) + \
                (vAngleToMarker2/30) * (self.focalLength30V - self.focalLength)     
            widthOfMarker1 = ((self.corners[self.index1][0][1][0] - self.corners[self.index1][0][0][0]) + \
                (self.corners[self.index1][0][2][0] - self.corners[self.index1][0][3][0])) / 2
            widthOfMarker2 = ((self.corners[self.index2][0][1][0] - self.corners[self.index2][0][0][0]) + \
                (self.corners[self.index1][0][2][0] - self.corners[self.index1][0][3][0])) / 2

            #distanceToAR = (knownWidthOfMarker(20cm) * focalLengthOfCamera) / pixelWidthOfMarker
            distanceToMarker1 = (self.knownMarkerWidth * realFocalLength1) / widthOfMarker1
            distanceToMarker2 = (self.knownMarkerWidth * realFocalLength2) / widthOfMarker2
            print(f"1: {distanceToMarker1}, 2: {distanceToMarker2}")
            self.distanceToMarker = (distanceToMarker1 + distanceToMarker2) / 2
    
        return True 
    '''
    id1 is the marker you want to look for
    specify id2 if you want to look for a gate
    set write to true to write out images to disk
    cameras=number of cameras to check. -1 for all of them
    '''
    def findMarker(self, id1, id2=-1, cameras=-1):
        if cameras == -1:
            cameras=len(self.caps)
            
        for i in range(cameras):
            ret, frame = self.caps[i].read()
            if self.markerFound(id1, frame, id2=id2): 
                return True

        return False
