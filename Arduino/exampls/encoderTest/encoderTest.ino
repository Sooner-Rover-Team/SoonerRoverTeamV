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
}

long position  = -999;

void loop() {
  long newPos;
  newPos = knob.read();
  Serial.println(newPos);

  if(angle1 == 0) { // out
    digitalWrite(4, HIGH);
    digitalWrite(5, LOW);
  }
  else if(angle1 == 2) { // in
    digitalWrite(4, LOW);
    digitalWrite(5, HIGH);
  }
  else {
    digitalWrite(4, HIGH);
    digitalWrite(5, HIGH);
  }

  // if a character is sent from the serial monitor,
  // reset both back to zero.
  // if (Serial.available()) {
  //   Serial.read();
  //   Serial.println("Reset both knobs to zero");
  //   knob.write(0);
  // }
}
