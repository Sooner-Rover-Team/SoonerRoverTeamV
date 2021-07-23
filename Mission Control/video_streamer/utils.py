import cv2
import datetime

# find the number of streams actively providing frames


def findactivestreams(vslist):
	activestreams = 0
	for vs in vslist:
		if vs.stopped == False:
			activestreams += 1
	return activestreams

# find number of video streams actively recording


def findrecording(vslist):
	recording = []
	for vs in vslist:
		recording.append(vs.recording)
	return recording

# takes a string of integers separated by commas and returns a list


def parseindicies(string):
	if ',' in string:
		splstring = string.split(',')
		indexlist = map(int, splstring)
		return indexlist
	else:
		return [int(string)]

# handlers for the currently connected cameras


def handlecamops(vslist, request, activestreams, recordingstreams, camerasconnected):
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
			vslist[i].relaunch()
		if 'startvs{}'.format(i+1) in request.form and activestreams <= 3:
			vslist[i].start()
		if 'movetoleft{}'.format(i+1) in request.form:
			temp = vslist.pop(i)
			vslist.insert(0, temp)

# grab the current timestamp and draw it on the frame


def timestampframe(frame):
	timestamp = datetime.datetime.now()
	copiedframe = frame.copy()
	cv2.putText(copiedframe, timestamp.strftime(
		"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
		cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
	return copiedframe

# essentially all this does is calculate the amount of time to wait
# before grabbing the next frame


def calcwait(difference, targettime, lastwait):
	timetosleep = lastwait - (difference-targettime)
	if timetosleep < 0:
		timetosleep = 0
	if timetosleep > targettime:
		timetosleep = targettime
	return timetosleep

# turn a resolution string into valid integers


def parseresolution(resstring):
	if resstring == 'max':
		return (10000, 10000)
	elif 'x' in resstring:
		res = resstring.split('x')
		width = int(res[0])
		height = int(res[1])
		return (width, height)
	else:
		return (640, 480)
