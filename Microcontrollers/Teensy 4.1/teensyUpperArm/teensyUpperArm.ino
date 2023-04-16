/*
 * The upperArm controls the pitch/yaw motor, the 360 wrist motor, and the claw motor. It receives CAN 
 *  msgs and then updates the three motors accordingly. Both motors will have encoders for PID.
 *  When a motor is moved and then stopped, PID is used to make sure the motor stays at that position regardless of load.
 *  
 *  The pitchYaw motor is a NEO 550 motor controlled by the SPARKMAX controller that uses PWM between 1000us-2000us
 *  The 360 motor is a brushed DC motor controlled by the TALON SRX that uses PWM between 1000us-2000us
 *  The claw motor is a small brushed DC motor controlled by a PWM motor driver. This will use AnalogOut to generate the signal
 */
//-----------------------------------------------------------------
#ifndef __IMXRT1062__
  #error "This sketch should be compiled for Teensy 4.x"
#endif
//-----------------------------------------------------------------

#include <ACAN_T4.h>
#include <PID_v2.h>
#include <Servo.h>
#include <Encoder.h>

#define PITCHYAW_PIN 3
#define WRISTROTATE_PIN 6
#define CLAW_CLOSE_PIN 4 // not working
#define CLAW_OPEN_PIN A5
#define DEBUG 1

//-----------------------------------------------------------------

Servo pitchYaw, wristRotate;
 //Encoder pitchYawEncoder(2, 3), clawEncoder(4, 5); //best if these are on interrupt pins
CANMessage message;

int pitchYawSpeed = 90;
int rotateSpeed = 90;
int clawSpeed = 126;

// PID
 double Kp1 = 2, Ki1 = 5, Kd1 = 1; // fine tuned values for each motor
 double Kp2 = 2, Ki2 = 5, Kd2 = 1;
 PID_v2 clawPID(Kp1, Ki1, Kd1, PID::Direct);
 PID_v2 pitchYawPID(Kp2, Ki2, Kd2, PID::Direct);
 boolean pitchYawPIDActive = false;
 boolean clawPIDActive = false;

//-----------------------------------------------------------------

void setup () {
  // Setup CAN/ Serial
  #if DEBUG
    pinMode (LED_BUILTIN, OUTPUT) ;
    Serial.begin (115200) ;
    while (!Serial) {
      delay (50) ;
      digitalWrite (LED_BUILTIN, !digitalRead (LED_BUILTIN)) ;
    }
  #endif
  ACAN_T4_Settings settings (100 * 1000) ; // 100 kbit/s - must agree on both ends of CAN

  const uint32_t errorCode = ACAN_T4::can3.begin (settings) ;

  if (0 == errorCode) {
    #if DEBUG
      Serial.println ("can3 ok") ;
    #endif
  }else{
    #if DEBUG
      Serial.print ("Error can3: 0x") ;
      Serial.println (errorCode, HEX) ;
    #endif
    while (1) {
      delay (100) ;
      #if DEBUG
        Serial.println ("Invalid setting") ;
      #endif
      digitalWrite (LED_BUILTIN, !digitalRead (LED_BUILTIN)) ;
    }
  }
  
  // set up servo objects for PWM generation and digital signals (0 or 1)
  pitchYaw.attach(PITCHYAW_PIN); //PWM pulse high time min/max = 900us-2100us
  wristRotate.attach(WRISTROTATE_PIN, 1000, 2000);
  pinMode(CLAW_CLOSE_PIN, OUTPUT);
  pinMode(CLAW_OPEN_PIN, OUTPUT);

  pitchYaw.writeMicroseconds(1500);
  wristRotate.write(rotateSpeed);
  digitalWrite(CLAW_CLOSE_PIN, LOW);
  digitalWrite(CLAW_OPEN_PIN, LOW);
}

void updateMotors() {
    //update variabels so PID can use this data too
  pitchYawSpeed = message.data[0];
  rotateSpeed = message.data[1];
  clawSpeed = message.data[2];
  
  //write to motors
  pitchYaw.writeMicroseconds(map(pitchYawSpeed, 0, 255, 1000, 2000));
  wristRotate.writeMicroseconds(map(rotateSpeed, 0, 255, 1000, 2000));
  if(clawSpeed > 130) {
    digitalWrite(CLAW_CLOSE_PIN, HIGH);
  }
  else if(clawSpeed < 120) {
    digitalWrite(CLAW_OPEN_PIN, HIGH);
  }
  else {
    digitalWrite(CLAW_CLOSE_PIN, LOW);
    digitalWrite(CLAW_OPEN_PIN, LOW);
  }
}

void loop () {
  if (ACAN_T4::can3.receive (message)) {
    #if DEBUG
    if(message.id == 0x02) {
      Serial.print("ID=");
      Serial.print(message.id);
      Serial.print(" msg = ");
      for(int i=0; i<message.len; ++i) {
        Serial.print(message.data[i]);
        Serial.print(", ");
      }
      Serial.println();
    }
    #endif

    if(message.id == 0x02) { // upperarm ID = 0x02
      if(message.len == 3) { // one byte for each motor
        updateMotors();
      }
    }
  }

  /***** PID WILL NEED TO BE TESTED AFTER SAR *****/

   //monitor motor position after writing using PID.
   //  once movement has stopped, we want motors to stay in place when force is applied
  //  if (pitchYawSpeed == 90) {
  //    if (!pitchYawPIDActive) {
  //      // Start PID using the stopped encoder position as the input value and set point
  //      pitchYawPID.Start(pitchYawEncoder.read(), 90, pitchYawEncoder.read()); // input, current value, set point
  //      pitchYawPIDActive = true;
  //    }
     
  //    // get the PID outputs
  //    const double pitchYawSpeedOutput = pitchYawPID.Run(pitchYawEncoder.read()); // run PID continuously based on encoder input
  //    pitchYaw.write(pitchYawSpeedOutput);
  //  }
  //  else if (pitchYawPID) { // if arm is moving, turn pid off.
  //    pitchYawPID = false;
  //  }
   
  //  if (clawSpeed == 90) {
  //    if (!clawPIDActive) {
  //      // Start PID using the stopped encoder position as the input value and set point
  //      clawPID.Start(clawEncoder.read(), 0, clawEncoder.read());
  //      clawPIDActive = true;
  //    }
  //    // get the PID outputs
  //    const double clawSpeedOutput = clawPID.Run(clawEncoder.read());
  //    claw.write(clawSpeedOutput);
  //  }
  //  else if (clawPIDActive) { // if arm is moving, turn pid off.
  //    clawPIDActive = false;
  //  }
}