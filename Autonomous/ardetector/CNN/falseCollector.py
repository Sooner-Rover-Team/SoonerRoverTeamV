import cv2
import argparse


def collectImages(args):
    cam = cv2.VideoCapture('\dev\video0')

    if not cam.isOpen():
        print('Error, cannot open that camera')
        exit(-1)

    cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)



    

def createParser():
    parser = argparse.ArgumentParser(description = 'Collects images that are assumed to not have an AR tag')
    parser.add_argument('-cam', type=str, default='/dev/video0', help='Camera file to be read from')
    parser.add_argument('-iterations', type=int, default=100, help='Number of images to take')
    parser.add_argument('-imageFile', type=str, default='TrainImages', help='Folder the images gets stored in')
    parser.add_argument('-labelFile', type=str, default='TrainBinaryLabels', help='Folder the true/false (stored as 0 or 1) label gets stored')
    parser.add_argument('-ArucuInImage', type=bool, default=True, help='If there is an ArUco marker in the image')
    
    return parser

if __name__ == "__main__":
    parser = createParser()
    args = parser.parse_args()
    collectImages(args)
