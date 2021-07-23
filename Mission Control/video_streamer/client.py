from flask import Response, Flask, render_template, request
import argparse
from videostream import VideoStream
from utils import findactivestreams, findrecording, parseindicies, handlecamops, calcwait, timestampframe
import imutils
import cv2
import time

# global variables to keep track of encoding quality and the targeted time between frames
encodingquality = 50
targetfps = 30	 # 30 FPS as a default
targetwait = 1000/targetfps  # in milliseconds
maxframesize = None  # the max width of the camera frame
framesize = 640  # 600px width default
videowidth = 600  # width of html video element

# initialize a flask object
app = Flask(__name__)


# define the root url to be index.html
# in other words, when the user accesses http://[ip]:[port]/
# they will see index.html
@app.route("/", methods=['GET', 'POST'])
def index():
    global encodingquality, targetwait, targetfps, framesize, videowidth, maxframesize
    if 'zoomslider' in request.form:
        videowidth = int(request.form['zoomslider'])
    # add button handler for the quality selector
    if 'qualitysubmit' in request.form:
        encodingquality = int(request.form['qualityslider'])

    # add button handler for the FPS buttons
    for i in [30, 20, 15, 12, 10, 8, 5, 4, 3, 2, 1]:
        if 'fps_{}'.format(i) in request.form:
            targetwait = 1000/i
            targetfps = i

    # add button handler for the frame size slider
    if 'sizesubmit' in request.form:
        framesize = int(request.form['sizeslider'])

    if 'zoomsubmit' in request.form:
        # do some shit wiht the value here
        pass

    # find active streams for limiting new streams
    activestreams = findactivestreams(vslist)
    recordingstreams = findrecording(vslist)
    camerasconnected = len(vslist)
    handlecamops(vslist, request, activestreams,
                 recordingstreams, camerasconnected)

    # find number of active video streams for rendering
    activestreams = findactivestreams(vslist)
    recordingstreams = findrecording(vslist)

    # return the rendered template
    return render_template("index.html",
                           camerasconnected=camerasconnected,
                           activestreams=activestreams,
                           encodingquality=encodingquality,
                           responsewait=targetwait,
                           fps=targetfps,
                           recordingstreams=recordingstreams,
                           framesize=framesize,
                           videowidth=videowidth,
                           maxframesize=maxframesize)


def generate():
    # grab global references to the list of video streams
    # and create list for frames to be stored in
    global vslist
    framelist = []

    # declare variables for calculating time differences
    lastwait = 0
    lasttime = time.time()

    # loop over frames from the output stream
    while True:
        # find difference in times between iterations
        currenttime = time.time()  # in seconds
        difference = (currenttime-lasttime)*1000  # in milliseconds
        lasttime = currenttime

        # calculate the projected time this function will take to execute
        calculatedwait = calcwait(
            difference, targetwait, lastwait)  # in milliseconds
        lastwait = calculatedwait

        # debugging stuff, dont delete yet lol
        # print('difference is ' + str(difference) + 'ms, trying to wait ' + str(targetwait) + 'ms, waiting ' + str(calculatedwait) + 'ms')

        time.sleep(calculatedwait/1000)  # sleep takes an argument in seconds

        # read a frame from each vs in vslist and add it
        # to framelist if it is readable
        for vs in vslist:
            if vs.isreadable():
                framelist.append(vs.read())

        # continue if there are no frames to read
        if len(framelist) == 0:
            continue

        # resize each frame to 600
        resizedlist = []
        for frame in framelist:
            resizedlist.append(imutils.resize(frame, width=framesize))

        # merge each of the three frames into one image
        mergedim = cv2.hconcat(resizedlist)

        # add the timestamp to the merged image
        mergedim = timestampframe(mergedim)

        # clear the framelist for the next iteration
        framelist.clear()

        # encode the frame in JPEG format
        encoding_parameters = [int(cv2.IMWRITE_JPEG_QUALITY), encodingquality]
        (flag, encodedimage) = cv2.imencode(
            ".jpg", mergedim, encoding_parameters)

        # ensure the frame was successfully encoded
        if not flag:
            continue

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedimage) + b'\r\n')

# return the generated image to the 'video_feed' element of index.html


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="port number of the server (1024 to 65535)")
    ap.add_argument("-r", "--resolution", type=str, default='640x480',
                    help='resolution of cameras (\'max\' for max resolution)')
    ap.add_argument("-s", "--source", type=str, default='-1',
                    help='indicies of cameras to use')

    # parse arguments
    args = vars(ap.parse_args())

    # create a list of video streams to reference in generate()
    vslist = []

    # find up to 10 attached cameras and try and start streams on them
    if args['source'] == '-1':
        print('shotgun approach')
        for i in range(0, 9):
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
        print('opening ' + args['source'])
        for i in sources:
            vs = VideoStream(i, 'vs{}'.format(i+1), args['resolution'])
            if vs.stream.isOpened() is False:
                vs.release()
            else:
                if maxframesize is None:
                    maxframesize = vs.width
                vslist.append(vs)

    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)

# release the video stream pointer
for vs in vslist:
    vs.release()
