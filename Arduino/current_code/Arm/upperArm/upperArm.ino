#define ENCODER_DO_NOT_USE_INTERRUPTS

#include <Servo.h>
#include <Encoder.h>
#include <SPI.h> 
#include <ACAN2515.h>
#include <PID_v2.h>
/*
 * The upperArm controls the pitch/yaw motor, the 360 wrist motor, and the claw motor. It receives CAN 
 *  msgs and then updates the three motors accordingly. Both motors will have encoders for PID.
 *  When a motor is moved and then stopped, PID is used to make sure the motor stays at that position regardless of load.
 *  
 *  The pitchYaw motor is a NEO 550 motor controlled by the SPARKMAX controller that uses PWM between 1000us-2000us
 *  The 360 motor is a brushed DC motor controlled by the TALON SRX that uses PWM between 1000us-2000us
 *  The claw motor is a small brushed DC motor controlled by a PWM motor driver. This will use AnalogOut to generate the signal
 */

 Servo pitchYaw, wristRotate;
 //Encoder pitchYawEncoder(2, 3), clawEncoder(4, 5); //best if these are on interrupt pins

 #define PITCHYAW_PIN 5
 #define WRISTROTATE_PIN 6
 #define CLAW_CLOSE_PIN 7
 #define CLAW_OPEN_PIN 8
 #define DEBUG 1

 int pitchYawSpeed = 90;
 int rotateSpeed = 90;
 int clawSpeed = 90;

// CAN Setup
static const byte MCP2515_CS = 10; // clock select pin
static const byte MCP2515_INT = 2; // interupt pin
ACAN2515 can(MCP2515_CS, SPI, MCP2515_INT);
static const uint32_t QUARTZ_FREQUENCY = 8UL * 1000UL * 1000UL; // 8 MHz crystral
CANMessage frame; // the object that will store the CAN data/ID


// PID
 double Kp1 = 2, Ki1 = 5, Kd1 = 1; // fine tuned values for each motor
 double Kp2 = 2, Ki2 = 5, Kd2 = 1;
 PID_v2 clawPID(Kp1, Ki1, Kd1, PID::Direct);
 PID_v2 pitchYawPID(Kp2, Ki2, Kd2, PID::Direct);
 boolean pitchYawPIDActive = false;
 boolean clawPIDActive = false;

void setup() {
  #if DEBUG
    Serial.begin(9600);
    Serial.println("Setting up...");
  #endif
  // setup for CAN
  SPI.begin();
  ACAN2515Settings settings(QUARTZ_FREQUENCY, 100UL * 1000UL); // 100 kb/s
  settings.mRequestedMode = ACAN2515Settings::NormalMode;
  const uint16_t errorCode = can.begin(settings, [] { can.isr(); });
  #if DEBUG // print error codes if can can't initialize
    if(errorCode == 0) {
        Serial.print("Actual bit rate: ");
        Serial.print(settings.actualBitRate());
    }
    else{
      Serial.print ("Configuration error 0x") ;
      Serial.println (errorCode, HEX) ;
    }
    Serial.println("CAN initialized");
  #endif

  //attachInterrupt(digitalPinToInterrupt(CAN_INT_PIN), MCP2515_ISR, FALLING);

   pitchYaw.attach(PITCHYAW_PIN, 900, 2100); //PWM pulse high time min/max = 900us-2100us
   wristRotate.attach(WRISTROTATE_PIN, 900, 2100);
   claw.attach(CLAW_PIN, 900, 2100);

   pitchYaw.write(pitchYawSpeed);
   claw.write(clawSpeed);
}

void updateMotors() {
    //update variabels so PID can use this data too
  pitchYawSpeed = frame.data[1];
  rotateSpeed = frame.data[2];
  clawSpeed = frame.data[3];
  
  //write to motors
  pitchYaw.write(map(pitchYawSpeed, 0, 255, 0, 180));
  wristRotate.write(map(rotateSpeed, 0, 255, 0, 180));
  if(clawSpeed > 130) {
    digitalWrite(CLAW_CLOSE_PIN, HIGH);
  }
  if(clawSpeed < 120) {
    digitalWrite(CLAW_OPEN_PIN, HIGH);
  }
  else {
    digitalWrite(CLAW_CLOSE_PIN, LOW);
    digitalWrite(CLAW_OPEN_PIN, LOW);
  }
}


void loop() {
  // CAN RX buff = [pitchYawSpeed, rotateSpeed, clawSpeed], frame.id=0x02
  if (can.available()) { // if a msg is ready to be received
    digitalWrite(13, HIGH); // status LED to know we are receiving msgs
    can.receive(frame); // fill frame with CAN msg
    #if DEBUG // print what we get
      Serial.print("ID = ");
      Serial.println(frame.id);
      Serial.print("Length = ");
      Serial.println(frame.len);
      for(int i=0; i<frame.len; ++i) {
        Serial.print(frame.data[i]);
        Serial.print(", ");
      }
      Serial.println();
    #endif
    if(frame.id == 0x02) { // upperarm ID = 0x02
      if(frame.len == 3) { // one byte for each motor
        updateMotors();
      }
    }
    digitalWrite(13, LOW);
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
