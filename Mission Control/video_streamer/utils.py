from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from videostream import VideoStream
# The above imports are used in type checking and have no impact
# at runtime
import cv2
import datetime
from flask import request as Request
from time import localtime
from numpy import ndarray as Frame


def log(message):
    # prints to console with a timestamp
    now = localtime()
    timestr = '[{}:{}:{}] '.format(str(now.tm_hour).zfill(
        2), str(now.tm_min).zfill(2), str(now.tm_sec).zfill(2))
    print(timestr + message)


def stream_info(vslist: list):
    # find the number of streams actively providing frames
    activestreams = 0
    maxframesize = 0
    recording = []
    for vs in vslist:
        recording.append(vs.recording)
        if vs.stopped == False:
            activestreams += 1
        maxframesize = max(maxframesize, vs.height)
    # active_streams = [v for v in vslist if v.stopped == False]
    return recording, activestreams, maxframesize


def findrecording(vslist: list) -> list:
    # find number of video streams actively recording
    recording = []
    for vs in vslist:
        recording.append(vs.recording)
    return recording


def parseindicies(string: str):
    # takes a string of integers separated by commas and returns a map
    # or a single integer
    if ',' in string:
        splstring = string.split(',')
        indexmap = map(int, splstring)
        return indexmap
    else:
        return [int(string)]


def handlecamops(vslist, request: Request, activestreams: int, recordingstreams: list, camerasconnected: int) -> None:
    # handlers for the currently connected cameras
    for i in range(0, camerasconnected):
        if 'stopvs{}'.format(i+1) in request.form:
            vslist[i].stop()
        if 'recordvs{}'.format(i+1) in request.form:
            if recordingstreams[i]:
                vslist[i].recordstop()
            else:
                vslist[i].recordstart()
        if 'startrecordvs{}'.format(i+1) in request.form:
            vslist[i].recordstart()
        if 'relaunchvs{}'.format(i+1) in request.form:
            res = request.form['relaunchvsres{}'.format(i+1)]
            vslist[i].relaunch(res)
        if 'startvs{}'.format(i+1) in request.form and activestreams <= 3:
            vslist[i].start()
        if 'movetoleft{}'.format(i+1) in request.form:
            temp = vslist.pop(i)
            vslist.insert(0, temp)
        if 'rotate{}'.format(i+1) in request.form:
            vslist[i].rotate()


def timestampframe(frame: Frame) -> Frame:
    # grab the current timestamp and draw it on the frame
    timestamp = datetime.datetime.now()
    copiedframe = frame.copy()
    cv2.putText(copiedframe, timestamp.strftime(
        "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    return copiedframe


def calcwait(difference: float, targettime: float, lastwait: float) -> float:
    # essentially all this does is calculate the amount of time to wait
    # before grabbing the next frame
    timetosleep = lastwait - (difference-targettime)
    if timetosleep < 0:
        timetosleep = 0
    if timetosleep > targettime:
        timetosleep = targettime
    return timetosleep


def parseresolution(resstring: str) -> tuple:
    # turn a resolution string into valid integers
    if resstring == 'max':
        return (10000, 10000)
    elif 'x' in resstring:
        res = resstring.split('x')
        width = int(res[0])
        height = int(res[1])
        return (width, height)
    else:
        return (640, 480)
