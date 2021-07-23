# Arduino Code for the Capstone Arms

This is the arm we were planing on using but could not.

Required libraries (install them from the built in library manager):
* EtherCard (1.1.0)
  * Only needed for using the Arduino Nano ethernet shield. The Uno-style shield (on the Megas) uses the built in ethernet library.
  * [GitHub](https://github.com/njh/EtherCard)

## Testing Programs

### rover_arm_test.ino

This is similar to *servo_test.ino* but made specifically for the rover's arm. It works the same way, except you can select which angle you want to drive.
What's new in this one is you can just spam the enter key in the console if you want it to stop moving in case you accidentally type 9 instead of 90.

### rover_arm_pid_test.ino

This works like the other arm test program except you type in an enocder value you want it to move to instead of a speed. *This is currently unfinished, so please do not use it for testing.*

The "PID.h" files are based on the [Arduino PID library](https://playground.arduino.cc/Code/PIDLibrary/) made by Brett Beauregard. ([Github page](https://github.com/br3ttb/Arduino-PID-Library/)) The only change I've made is the addition of a function to reset the intergral term of the PID.

## Rover Programs

### control_arm.ino

For the control arm's Arduino Mega (with ethernet shield).

### rover_arm.ino

For the rover arm's Arduino Mega (with ethernet shield). Incomplete, currently behind in updates compared to *rover_arm_test.ino*
