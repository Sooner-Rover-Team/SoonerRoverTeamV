#include <Servo.h>
#include <Encoder.h>
/*
 * The upperArm controls the pitch/yaw motor and the claw motor. It receives CAN 
 *  msgs and then updates the two motors accordingly. Both motors will have encoders for PID.
 *  When a motor is moved, PID is used to make sure the motor stays at that position regardless of load.
 *  
 *  Both motors are normal DC motors, so small PWM motor controllers will be used
 *  
 *  I currently do not know what arduino will be used or what controllers will be used for the motors.
 */

 Servo pitchYaw, claw
 Encoder pitchYawEncoder(2, 3), clawEncoder(4, 5); //best if these are on interrupt pins

 #define PITCHYAW_PIN 5
 #define CLAW_PIN 6

 int pitchYawSpeed = 90;
 int clawSpeed = 90;


void pid() {
   // get current motor positions 
   int pitchYawPosition = pitchYawEncoder.read();
   int clawPosition = clawEncoder.read();

   //Some PID stuff to keep motors at that position
}

void receiveCAN() {
  //decode stuff

  //update variabels (this step may not be necessary but could help with trouble shooting at some point)

  //write to motors

  //monitor motor position after writing using PID. make sure position does not move
  pid();
}

void setup() {
  pitchYaw.attach(PITCHYAW_PIN, 900, 2100); //PWM pulse high time min/max = 900us-2100us
  claw.attach(CLAW_PIN, 900, 2100);

  pitchYaw.write(pitchYawSpeed);
  claw.write(clawSpeed);
}

void loop() {
  // Not exactly sure how CAN receives data, but when a msg is ready, call this function to decode
  if (/*msg has arrived*/) {
    receiveCAN();
  }

}
