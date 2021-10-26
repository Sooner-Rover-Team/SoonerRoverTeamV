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
        cv.cvtColor(src=image, code=cv.COLOR_RGB2GRAY, dest=image) 
        # tries converting to b&w using different different cutoffs to find the perfect one for the ar tag
        for i in range(40, 221, 60):
            aruco.detectMarkers((image > i), self.tagDict, corners, MarkerIDs, parameters, rejects) 
            if(MarkerIDs.size() > 0)
             
                if(MarkerIDs.size() == 1)
                 
                    std::cout << "Just found one post" << std::endl 
                 
                else
                 
                    if(writeToFile)
                     
                        mFrame = image > i  # purely for debug
                        videoWriter.write(mFrame)  # purely for debug
                     
                    break 
                 
             
            if(i == 220) # did not ever find two ars. TODO add something for if it finds one tag
             
                if(writeToFile)
                    videoWriter.write(image) 
                distanceToAR = -1 
                angleToAR = 0 
                return 0 
             
         
        int index1 = -1, index2 = -1 
        for(int i = 0  i < MarkerIDs.size()  i++) # this just checks to make sure that it found the right tags
         
            if(MarkerIDs[i] == id1 || MarkerIDs[i] == id2)
             
                if(MarkerIDs[i] == id1)
                    index1 = i 
                else
                    index2=i  
                if(index1 != -1 && index2 != -1)
                    break 
                
         
        if(index1 == -1 || index2 == -1) 
         
            distanceToAR=-1 
            angleToAR=0 
            std::cout << "index1: " << index1 << "\nindex2: " << index2 << std::endl 
            if(index1 != -1 || index2 != -1)
             
                return 1 
             
            return 0  # no correct ar tags found
         
        else
         
            widthOfTag1 = corners[index1][1].x - corners[index1][0].x 
            widthOfTag2 = corners[index2][1].x - corners[index2][0].x 

            # distanceToAR = (knownWidthOfTag(20cm) * focalLengthOfCamera) / pixelWidthOfTag
            distanceToAR1 = (knownTagWidth * focalLength) / widthOfTag1 
            distanceToAR2 = (knownTagWidth * focalLength) / widthOfTag2 
            std::cout << "1: " << distanceToAR1 << "\n2: " << distanceToAR2 << std::endl 
            std::cout << "focal: " << focalLength << "\nwidth: " << widthOfTag << std::endl 
            distanceToAR = (distanceToAR1 + distanceToAR2) / 2 
            std::cout << distanceToAR << std::endl 
        
            centerXTag = (corners[index1][1].x + corners[index2][0].x) / 2 
            angleToAR = degreesPerPixel * (centerXTag - 960)  # takes the pixels from the tag to the center of the image and multiplies it by the degrees per pixel
        
            return 2 
         


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
