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
// Servo motor;
//   avoid using pins with LEDs attached

void setup() {
  Serial.begin(9600);
  Serial.println("TwoKnobs Encoder Test:");

}

long newPos = 0;


void loop() {

  long newPos;
  newPos = knob.read();
  Serial.println(newPos);
}
