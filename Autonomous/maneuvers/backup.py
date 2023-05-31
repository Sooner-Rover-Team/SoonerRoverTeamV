from libs import Drive
import argparse

# Take camera sources as an arguement
argParser = argparse.ArgumentParser()
argParser.add_argument("cameraInput", type=int, help="takes a number representing which camera to use")
args = argParser.parse_args()

if __name__ == "__main__":
    #user input (args from system)
    if args.cameraInput is None:
        print("ERROR: must at least specify one camera")
        exit(-1)
    
    # Create a rover object
    rover = Drive.Drive(50, args.cameraInput)

    rover.backupManeuver()