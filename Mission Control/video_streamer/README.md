# RoverCam Python

The video streamer is written in python. It requires python3 version >=3.8.5, 4 libraries, and creation of a virtual environment.

## Setting Up A Virtual Environment

Linux only: install virtual environments with

```bash
sudo apt-get install python3-venv
```

Make sure you are in /SoRo-19-20/Mission Control/video_streamer/ then run

```bash
python3 -m venv .venv
```

This will create a new virtual environment in /video_streamer/. The virtual environment must be activated every time the program needs to be run which can be done with:

Linux:

```bash
source .venv/bin/activate
```

Windows (Powershell):

```powershell
.venv/Scripts/Activate.ps1
```

---

## Installing Packages

Next, these four packages need to be installed

- wheel
- imutils
- flask
- opencv-contrib-python

install these with

```bash
python3 -m pip install wheel opencv-contrib-python flask
```

The imutils package needs to be installed after wheel:

```bash
python3 -m pip install imutils
```

---

## Usage

To run, use

```bash
python3 client.py -i [ip of the device] -o [port] --resolution "{width}x{height}" --source 1,2,3
```

and navigate to that ip from another device.

### Notes on Usage

The program will automatically look for up to 10 cameras on launch, but only 3 simultaneous streams are supported for bandwidth considerations. Additionally, specific camera indices can be specified through an argument. 

The resolution of cameras can be set via an argument. The default resolution is 640 by 480 but any resolution can be set by passing in a string such as "1280x720". "max" can also be passed as a resolution to set the cameras to their maximum resolution. Recordings from each camera can be started and will be saved to ./recordings/recording.avi. The quality and framerate can both be adjusted during runtime.

Each stream can also be relaunched, which disposes of the current VideoCapture and VideoWriter object and creates new instances. This could be useful in case of a hardware error with a USB camera; the program can reaccess the camera without fully restarting. It also has the side effect of saving any recordings that had been captured up to that point in the execution.
