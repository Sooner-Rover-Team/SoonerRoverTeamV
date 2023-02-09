from threading import Thread
import cv2
import datetime
import time
import os
from numpy import ndarray as Frame
from utils import calcwait, timestampframe, parseresolution, log
# from imutils import rotate

ROTATE_ENUM = [0, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]

class VideoStream:
    # initialize self with defined source and fps
    def __init__(self, src=0, name="VideoStream", resolution='640x480'):
        # set grabbed to false
        self.grabbed: bool = False

        # define a variable to indeicate whether recording should happen
        self.recording: bool = False

        # set the name of the object
        self.name: str = name

        # define a variable to indicate whether the thread should be stopped
        self.stopped: bool = True

        # initialize the VideoCapture object with the source
        self.stream: cv2.VideoCapture = cv2.VideoCapture(src)

        if self.stream.isOpened():
            log('opened ' + self.name)

        # try setting width and height to the arguments passed
        (self.width, self.height) = parseresolution(resolution)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # set the capture codec to MJPG
        self.stream.set(cv2.CAP_PROP_FOURCC,
                        cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

        # gets actual width and height from camera
        self.width = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # gets actual fps value from camera
        self.fps = self.stream.get(cv2.CAP_PROP_FPS)

        # creates a new VideoWriter to save the recording
        currenttime: datetime.datetime = datetime.datetime.now()
        self.filename = './recordings/{}_{}.avi'.format(
            currenttime.strftime("%Y%m%d_%H-%M-%S"), self.name)
        self.writer = cv2.VideoWriter(self.filename, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), self.fps, (self.width, self.height))

        # saves the index of the webcam for relaunching
        self.src = src
        self.totaldifference = 0
        self.recordedframes = 0
        # time in milliseconds between each frame
        if self.fps != 0:
            self.waittime = 1000/self.fps

        self.rotation = 0

    def start(self) -> None:
        # create a new thread to continuously call update() and read frames
        if self.stopped is True:
            log('starting ' + self.name)
            self.stopped = False
            t = Thread(target=self.update, name=self.name, args=())
            t.daemon = True
            t.start()
            # log('thread started')
        else:
            log(self.name + " is already running")

    def update(self) -> None:
        # read a frame from the camera unless stopped is true
        while True:
            if self.stopped:
                self.grabbed = False
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the most recent frame grabbed from the camera
        # rotate the frame first if need be
        if self.rotation != 0:
            rotate_val = ROTATE_ENUM[self.rotation]
            frame = cv2.rotate(self.frame, rotate_val)
            return frame
        else:
            return self.frame

    def stop(self) -> None:
        # set stopped to True which will halt the thread
        log('stopping ' + self.name)
        self.recordstop()
        self.stopped = True

    def set(self, property, value) -> None:
        # sets the property of the VideoCapture object
        self.stream.set(property, value)

    def get(self, property) -> property:
        # returns the property of the VideoCapture object
        return self.stream.get(property)

    def isreadable(self) -> bool:
        # returns whether a frame can be read
        return self.grabbed

    def getsrc(self) -> int:
        # returns index of camera
        return self.src

    def release(self) -> None:
        # releases video capture object
        self.stop()
        self.writer.release()
        self.stream.release()
        time.sleep(.1)
        if os.path.exists(self.filename) and os.stat(self.filename).st_size < 10000:
            os.remove(self.filename)

    def relaunch(self, res='max') -> None:
        # releases old VideoCapture object and creates a new one
        # use this if there's a hardware error with the camera such
        # as it being unplugged while the program is running
        log('relaunch has been called with res ' + str(res))
        self.release()
        self.__init__(self.src, self.name, res)

    def recordstart(self) -> None:
        # starts the thread that handles recording
        if self.recording == False and self.stopped == False:
            self.recording = True
            log('recording started')
            t = Thread(target=self.record, name=(
                self.name + 'record'), args=())
            t.daemon = True
            t.start()
        else:
            log('recording has already started')

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4

    def record(self) -> None:
        # target function to grab a frame from the camera after a set amount of time
        lasttime = time.time()
        lastwait = 0
        while True:
            if self.recording == False:
                return
            if self.stopped == False:
                self.writer.write(timestampframe(self.read()))
                currenttime = time.time()
                difference = (currenttime-lasttime)*1000
                lasttime = currenttime
                # debugging stuff
                # self.totaldifference += difference
                # self.recordedframes += 1

                timetosleep = calcwait(difference, self.waittime, lastwait)
                lastwait = timetosleep
                # log('difference: ' + str(difference) + ' going to wait ' + str(timetosleep) + 'ms')
                time.sleep(timetosleep/1000)

    def recordstop(self) -> None:
        # stops the thread that handles recording
        if self.recording == True:
            log('recording stopped')
            self.recording = False
        else:
            log('recording is already stopped')
