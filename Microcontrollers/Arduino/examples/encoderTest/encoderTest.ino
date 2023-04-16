/* Encoder Library - TwoKnobs Example
 * http://www.pjrc.com/teensy/td_libs_Encoder.html
 *
 * This example code is in the public domain.
 */

#include <Encoder.h>
#include <Servo.h>

long lastPosition = 0;
bool stopped = false;
bool oscillate = false;
int angle1 = 2;

// Change these pin numbers to the pins connected to your encoder.
//   Best Performance: both pins have interrupt capability
//   Good Performance: only the first pin has interrupt capability
//   Low Performance:  neither pin has interrupt capability
Encoder knob(2, 3);
Servo motor;
//   avoid using pins with LEDs attached

void setup() {
  Serial.begin(9600);
  Serial.println("TwoKnobs Encoder Test:");
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  motor.attach(6, 900, 2100);
  motor.write(95);
}

long position  = -999;

void loop() {
  Serial.println("Input 0-180 to control the angle of the motor");
  // get the value the user inputs
  while (Serial.available() == 0) {}// this waits for someone to press enter with text in the Serial input.
  String userInput1 = Serial.readString(); // read the text (given by the user) as a String object.
  int angle1 = userInput1.toInt(); // convert the String into an int (integer) variable.
  Serial.println(angle1); // print the number to the Serial Monitor. (used for debugging)

  Serial.println("0,1,2 to control claw");
 // get the value the user inputs
 while (Serial.available() == 0) {}// this waits for someone to press enter with text in the Serial input.
 String userInput2 = Serial.readString(); // read the text (given by the user) as a String object.
 int angle2 = userInput2.toInt(); // convert the String into an int (integer) variable.
 Serial.println(angle2); // print the number to the Serial Monitor. (used for debugging)

  long newPos;
  newPos = knob.read();
  Serial.println(newPos);

  if(angle2 == 0) { // out
    digitalWrite(4, HIGH);
    digitalWrite(5, LOW);
  }
  else if(angle2 == 2) { // in
    digitalWrite(4, LOW);
    digitalWrite(5, HIGH);
  }
  else {
    digitalWrite(4, HIGH);
    digitalWrite(5, HIGH);
  }

  motor.write(angle1); 

  // if a character is sent from the serial monitor,
  // reset both back to zero.
  // if (Serial.available()) {
  //   Serial.read();
  //   Serial.println("Reset both knobs to zero");
  //   knob.write(0);
  // }
}
