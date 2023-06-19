from flask import Response, Flask, render_template, request
import argparse
import configparser
from videostream import VideoStream
from utils import stream_info, findrecording, parseindicies, handlecamops, calcwait, timestampframe, log
import imutils
from numpy import ndarray as Frame
import cv2
import time
import os

# global variables to keep track of encoding quality and the targeted time between frames
encodingquality = 50
targetfps = 30	 # 30 FPS as a default
target_wait = 1000/targetfps  # in milliseconds
maxframesize = None  # the max width of the camera frame
framesize = 640  # 600px width default
videowidth = 600  # width of html video element
MAX_CAMERAS = 10 # number of cameras to try opening if none are defined

# initialize a flask object
app = Flask(__name__)



@app.route("/", methods=['GET', 'POST'])
def index():
    # define the root url to be index.html
    # in other words, when the user accesses http://[ip]:[port]/
    # they will see index.html
    global encodingquality, target_wait, targetfps, framesize, videowidth, maxframesize
    if 'zoomslider' in request.form:
        videowidth = int(request.form['zoomslider'])
    # add button handler for the quality selector
    if 'qualitysubmit' in request.form:
        encodingquality = int(request.form['qualityslider'])

    # add button handler for the FPS buttons
    for i in [30, 20, 15, 12, 10, 8, 5, 4, 3, 2, 1]:
        if 'fps_{}'.format(i) in request.form:
            target_wait = 1000/i
            targetfps = i

    # add button handler for the frame size slider
    if 'sizesubmit' in request.form:
        framesize = int(request.form['sizeslider'])

    # find active streams for limiting new streams
    recordingstreams, activestreams, maxframesize = stream_info(vslist)
    
    camerasconnected: int = len(vslist)
    handlecamops(vslist, request, activestreams,
                 recordingstreams, camerasconnected)

    # find number of active video streams for rendering
    recordingstreams, activestreams, maxframesize = stream_info(vslist)

    # return the rendered template
    return render_template("index.html",
                           camerasconnected=camerasconnected,
                           activestreams=activestreams,
                           encodingquality=encodingquality,
                           responsewait=target_wait,
                           fps=targetfps,
                           recordingstreams=recordingstreams,
                           framesize=framesize,
                           videowidth=videowidth,
                           maxframesize=maxframesize)


def generate():
    # grab global references to the list of video streams
    # and create list for frames to be stored in
    global vslist
    framelist: list[Frame] = []

    # declare variables for calculating time differences
    lastwait = 0
    last_time = time.perf_counter()/1_000

    # loop over frames from the output stream
    while True:
        # read a frame from each vs in vslist and add it
        # to framelist if it is readable
        for vs in vslist:
            if vs.isreadable():
                frame = vs.read()
                framelist.append(frame)
                # print(frame.shape)

        # continue if there are no frames to read
        if len(framelist) == 0:
            continue

        # resize each frame to 600
        resizedlist: list = []
        for frame in framelist:
            resizedlist.append(imutils.resize(frame, height=framesize))

        # merge each of the three frames into one image
        mergedim: Frame = cv2.hconcat(resizedlist)

        # add the timestamp to the merged image
        mergedim = timestampframe(mergedim)

        # clear the framelist for the next iteration
        framelist.clear()

        # encode the frame in JPEG format
        encoding_parameters: list[int] = [
            int(cv2.IMWRITE_JPEG_QUALITY), encodingquality]
        (flag, encodedimage) = cv2.imencode(
            ".jpg", mergedim, encoding_parameters)

        # ensure the frame was successfully encoded
        if not flag:
            continue

        # find difference in times between iterations
        current_time = time.perf_counter()/1_000 # in milliseconds
        # difference = (currenttime-lasttime)*1000  # in milliseconds
        future_time = last_time + target_wait
        calculated_wait = future_time - current_time if future_time - current_time > 0 else 0
        last_time = current_time

        # debugging stuff, dont delete yet lol
        # log('difference is ' + str(current_time - last_time) + 'ms, trying to wait ' + str(target_wait) + 'ms, waiting ' + str(calculated_wait) + 'ms')

        time.sleep(calculated_wait/1000)  # sleep takes an argument in seconds

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedimage) + b'\r\n')


@app.route("/video_feed")
def video_feed() -> Response:
    # return the generated image to the 'video_feed' element of index.html
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


# check to see if this is the main thread of execution
if __name__ == '__main__':
    """ Change the current directory so config loads right """
    if os.path.dirname(__file__) != '':
        current_folder = os.path.dirname(__file__)
        os.chdir(current_folder)
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    config = configparser.ConfigParser()
    ap.add_argument("-i", "--ip", type=str, default=-1,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, default=-1,
                    help="port number of the server (1024 to 65535)")
    ap.add_argument("-r", "--resolution", type=str, default='max',
                    help='resolution of cameras (\'max\' for max resolution)')
    ap.add_argument("-s", "--source", type=str, default='-1',
                    help='indicies of cameras to use')

    # parse arguments
    args = vars(ap.parse_args())

    if args['ip'] == -1:
        config.read('config.ini')
        ip = config['Connection']['HOST']
        port = config['Connection']['PORT']
    else:
        ip = args["ip"]
        port = args["port"]

    # create a list of video streams to reference in generate()
    vslist = []

    # find up to MAX_CAMERAS attached cameras and try and start streams on them
    if args['source'] == '-1':
        log('shotgun approach')
        for i in range(0, MAX_CAMERAS-1):
            vs = VideoStream(i, 'vs{}'.format(i+1), args['resolution'])
            if vs.stream.isOpened() is False:
                vs.release()
            else:
                if maxframesize is None:
                    maxframesize = vs.width
                vslist.append(vs)
    # open cameras based on arguments passed
    else:
        sources = parseindicies(args['source'])
        log('opening ' + args['source'])
        for i in sources:
            vs = VideoStream(i, 'vs{}'.format(i+1), args['resolution'])
            if vs.stream.isOpened() is False:
                vs.release()
            else:
                if maxframesize is None:
                    maxframesize = vs.width
                vslist.append(vs)

    # start the flask app
    app.run(host=ip, port=port, debug=True,
            threaded=True, use_reloader=False)

# release the video stream pointer
for vs in vslist:
    vs.release()
