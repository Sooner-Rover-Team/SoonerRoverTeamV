#include <Servo.h>
/*
 * The lower Arm arduino sits in the arm Ebox and is responsible for controlling the base motor, 
 *  the two linear actuators (bicep/forearm), and the 360 wrist motor. The actuators act like servos
 *  while the base/360 motor will likely be controlled by TALONS, which use PWM speed control.
 */

Servo base, wrist, bicep, forearm

#define BASE_PIN 5
#define WRIST_PIN 6
#define BICEP_PIN 9
#define FOREARM_PIN 10

int baseSpeed = 90;
int wristSpeed = 90;
int bicepPosition = 180;
int forearmPosition = 180;


// not exactly sure how CAN receives data, but when a msg is received, decode and store data to variables.
void receiveCAN() {
  // decode stuff

 // update variables (this step may not be necessary but could help with trouble shooting at some point)
 baseSpeed = 0;
 wristSpeed = 0;
 bicepPosition = 0;
 forearmPosition = 0;

 // write to motors
  base.write(bicepSpeed);
  wrist.write(wristSpeed);
  bicep.write(bicepPosition);
  forearm.write(forearmPosition); 
}

void setup() {
  // not sure of which microcontroller right now. I vote arduino nano (only cuz I've used it a lot)
  // NANO PWM pins: D3, D5, D6, D9, D10, D11
  base.attach(BASE_PIN, 900, 2100); // PWM min/max pulse duration = 900us - 2100us
  wrist.attach(WRIST_PIN, 900, 2100);
  bicep.attach(BICEP_PIN, 900, 2100);
  forearm.attach(OREARM_PIN, 900, 2100);

  // initial speed/position of motors
  base.write(bicepSpeed);
  wrist.write(wristSpeed);
  bicep.write(bicepPosition);
  forearm.write(forearmPosition);
}

void loop() {
  // continuously wait for CAN msgs.
  if(/*msg is received*/){
    receiveCAN();
  }

}
