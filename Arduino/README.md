# Arduino Code :100:

Required libraries (install them from the built in library manager):
* EtherCard (1.1.0)
  * Only needed for using the Arduino Nano ethernet shield. The Uno-style shield (on the Megas) uses the built in ethernet library.
  * [GitHub](https://github.com/njh/EtherCard)

The "capstone arm" folder is full of other Arduino programs that were indended for the belt driven arm we did not end up using.

## Testing Programs

### servo_test.ino

This program is good for calibrating/testing a single talon (our motor controller).
To use it, change `#define PIN_SERVO 31` to whatever Arduino pin you're connecting the signal wire to, upload the code, and then open the serial monitor.
When you send a number to the Arduino it will write it to the servo.
When calibrating, use the range 10 to 170 instead of the full 0 to 180 because it freaks out the talons. 90 degrees will be still.

## Rover Programs

### wheel_controller.ino

This should be uploaded to the Arduino Nano in the e-box. The macro `#define DEBUG_MODE 0` can enable serial debugging messages. Don't use this when running the rover because it can cause the Arduino to randomly reset.

### arm_controller.ino

This is the code for the Arduino Nano controlling the currently used arm (the one with linear actuators). Like the wheel controller, it also has the optional debug macro.
