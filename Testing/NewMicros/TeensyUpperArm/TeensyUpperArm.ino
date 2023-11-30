/*
 * The upperArm controls the pitch/yaw motor, the 360 wrist motor, and the claw motor. It receives CAN 
 *  msgs and then updates the three motors accordingly. Both motors will have encoders for PID.
 *  When a motor is moved and then stopped, PID is used to make sure the motor stays at that position regardless of load.
 *  
 *  The pitch motor is a NEO 550 motor controlled by the SPARKMAX controller that uses PWM between 1000us-2000us
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
#include <HCSR04.h>
#include <EEPROM.h>

#define pitch_PIN 3
#define WRISTROTATE_PIN 4
#define CLAW_CLOSE_PIN 5 // not working
#define CLAW_OPEN_PIN 6
#define DEBUG 0 // 0 to run with no debugs, 1 to run with debugs
#define WRIST_PITCH_PIN1 7 // Used to read the wrists pitch.
#define WRIST_PITCH_PIN2 8
#define EBOX 0x04 // Unused CAN to send to the E-box

//UltraSonicDistanceSensor distanceSensor(9,10); // Pins 9 & 10 for the USDS

//-----------------------------------------------------------------

Servo pitch, wristRotate;
 //Encoder pitchEncoder(2, 3), clawEncoder(4, 5); //best if these are on interrupt pins
CANMessage recMessage; // Globally declares a CANMessage as message for receiving
CANMessage sendMessage; // Globally declares a CANMessage as message for sending

Encoder upperMotor(WRIST_PITCH_PIN1, WRIST_PITCH_PIN2); // Initializes the upper motor encoder

float USDSdistance = 0;  // Initializes a variable for the UltraSonicDistanceSensor
float USDSdistanceRepeat = 0; // Repeat variable for the UltraSonicDistanceSensor
int pitchMovement = 90;
int rotateMovement = 90;
int clawMovement = 126;
int wristPitch = 0; // Initializes the wrists yaw.
int wristPitchRepeat = 0;
int checkSum = 0; // Integer required for sending a CAN message

// PID
 double Kp1 = 2, Ki1 = 5, Kd1 = 1; // fine tuned values for each motor
 double Kp2 = 2, Ki2 = 5, Kd2 = 1;
 PID_v2 clawPID(Kp1, Ki1, Kd1, PID::Direct);
 PID_v2 pitchPID(Kp2, Ki2, Kd2, PID::Direct);
 boolean pitchPIDActive = false;
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
      Serial.println ("Error can3: 0x") ;
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
  pitch.attach(pitch_PIN, 1000, 2000); //PWM pulse high time min/max = 900us-2100us
  wristRotate.attach(WRISTROTATE_PIN, 1000, 2000);
  pinMode(CLAW_CLOSE_PIN, OUTPUT);
  pinMode(CLAW_OPEN_PIN, OUTPUT);

  pitch.writeMicroseconds(1500);
  wristRotate.write(rotateMovement);
  digitalWrite(CLAW_CLOSE_PIN, LOW);
  digitalWrite(CLAW_OPEN_PIN, LOW);

  // Sets up pins to read the wrist pitch
  pinMode (7, INPUT);
  pinMode (8, INPUT);
}

void sendWristInfo(int encoderValue, float distanceValue) {
  // Sends the wristPitch and USDSdistance as a CAN message to the EBOX Teensy.
  // encoderValue and distanceValue are used since to avoid name overlap with globally defined variables
  sendMessage.id = EBOX; // To EBOX (hex value)
  sendMessage.len = 2; // Indicates two values are being sent
  sendMessage.data[0] = encoderValue % 255; // Sets the first value encoderValue
  sendMessage.data[1] = encoderValue / 255; // Sets the second value to USDSdistance

  bool ok = ACAN_T4::can3.tryToSend(sendMessage);
  if(ok && DEBUG) {
    Serial.print("Wrist info ");
    Serial.print(sendMessage.data[1] * 255 + sendMessage.data[0]);
    Serial.println(" sent.");
  }
}

void updateMotors(CANMessage message) { // recieves a message and controls the motors
    // update variables so PID can use this data too
  pitchMovement = message.data[0];
  rotateMovement = message.data[1];
  clawMovement = message.data[2];

  // Writes the received CAN values to the motors
  pitch.write(map(pitchMovement, 0, 255, 0, 180));
  wristRotate.write(map(rotateMovement, 0, 255, 0, 180));
  if(clawMovement > 130) {
    digitalWrite(CLAW_CLOSE_PIN, HIGH);
  }
  else if(clawMovement < 120) {
    digitalWrite(CLAW_OPEN_PIN, HIGH);
  }
  else {
    digitalWrite(CLAW_CLOSE_PIN, LOW);
    digitalWrite(CLAW_OPEN_PIN, LOW);
  }
}

void loop () {
  if (ACAN_T4::can3.receive (recMessage)) {
    #if DEBUG
    if(recMessage.id == 0x02) {
      Serial.print("ID=");
      Serial.print(recMessage.id);
      Serial.print(" msg = ");
      for(int i=0; i<recMessage.len; ++i) {
        Serial.print(recMessage.data[i]);
        Serial.print(", ");
      }
      Serial.println();
    }
    #endif

    if(recMessage.id == 0x02) { // upperarm ID = 0x02
      if(recMessage.len == 3) { // one byte for each motor
        updateMotors(recMessage);
      }
    }
  }

  USDSdistance = 0; //distanceSensor.measureDistanceCm();
  wristPitch = upperMotor.read();

  #if DEBUG
    if (USDSdistance != USDSdistanceRepeat) {
      // Only displays the USDSdistance if it changes
      Serial.print("Distance in cm: ");
      Serial.println(USDSdistance);
    }
    USDSdistanceRepeat = USDSdistance;
    
    if (wristPitch != wristPitchRepeat) { 
      // Only displays the wristPitch if it changes
      Serial.print("Encoder value: ");
      Serial.println(wristPitch);
    }
    wristPitchRepeat = wristPitch;

  #endif

  sendWristInfo(wristPitch, USDSdistance);
}

/***** PID WILL NEED TO BE TESTED AFTER SAR *****/

   //monitor motor position after writing using PID.
   //  once movement has stopped, we want motors to stay in place when force is applied
  //  if (pitchMovement == 90) {
  //    if (!pitchPIDActive) {
  //      // Start PID using the stopped encoder position as the input value and set point
  //      pitchPID.Start(pitchEncoder.read(), 90, pitchEncoder.read()); // input, current value, set point
  //      pitchPIDActive = true;
  //    }
     
  //    // get the PID outputs
  //    const double pitchMovementOutput = pitchPID.Run(pitchEncoder.read()); // run PID continuously based on encoder input
  //    pitch.write(pitchMovementOutput);
  //  }
  //  else if (pitchPID) { // if arm is moving, turn pid off.
  //    pitchPID = false;
  //  }
   
  //  if (clawMovement == 90) {
  //    if (!clawPIDActive) {
  //      // Start PID using the stopped encoder position as the input value and set point
  //      clawPID.Start(clawEncoder.read(), 0, clawEncoder.read());
  //      clawPIDActive = true;
  //    }
  //    // get the PID outputs
  //    const double clawMovementOutput = clawPID.Run(clawEncoder.read());
  //    claw.write(clawMovementOutput);
  //  }
  //  else if (clawPIDActive) { // if arm is moving, turn pid off.
  //    clawPIDActive = false;
  //  }