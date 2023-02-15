#define ENCODER_DO_NOT_USE_INTERRUPTS

#include <Servo.h>
#include <Encoder.h>
#include <SPI.h> 
#include <mcp2515_can.h>
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
 Encoder pitchYawEncoder(2, 3), clawEncoder(4, 5); //best if these are on interrupt pins

 #define PITCHYAW_PIN 5
 #define WRISTROTATE_PIN 6
 #define CLAW_PIN A0

 int pitchYawSpeed = 90;
 int rotateSpeed = 90;
 int clawSpeed = 90;

 // CAN RX buff = [0x02, pitchYawSpeed, rotateSpeed, clawSpeed, checksum]
const int SPI_CS_PIN = 10;
const int CAN_INT_PIN = 2;
mcp2515_can CAN(SPI_CS_PIN);
unsigned char flagReceive = 0;
unsigned char len = 5;
unsigned char buff[5];
char str[20];


// PID
 double Kp1 = 2, Ki1 = 5, Kd1 = 1; // fine tuned values for each motor
 double Kp2 = 2, Ki2 = 5, Kd2 = 1;
 PID_v2 clawPID(Kp1, Ki1, Kd1, PID::Direct);
 PID_v2 pitchYawPID(Kp2, Ki2, Kd2, PID::Direct);
 boolean pitchYawPIDActive = false;
 boolean clawPIDActive = false;

void updateMotors() {
  Serial.println("CAN msg received: ");
  for(int i=0; i<len; ++i) {
    Serial.print(buff[i]);
    Serial.print(' ');
  }
  Serial.println();
  //decode stuff
  pitchYawSpeed = buf[1];
  rotateSpeed = buf[2];
  clawSpeed = buf[3];
  //update variabels (this step may not be necessary but could help with trouble shooting at some point)
  
  //write to motors
  pitchYaw.write(map(pitchYawSpeed, 0, 255, 0, 180));
  wristRotate.write(map(rotateSpeed, 0, 255, 0, 180));
  analogWrite(CLAW_PIN, map(0, 251, 0, 1024)); // can it go in reverse..?
}

void setup() {
  Serial.begin(9600);
  Serial.println("Setting up...");
  // setup for CAN
  attachInterrupt(digitalPinToInterrupt(CAN_INT_PIN), MCP2515_ISR, FALLING);
  // initialize can bus with 500kHz baudrate
  while (CAN_OK != CAN.begin(CAN_500KBPS)) {
    Serial.println("CAN init fail, retry...");
    delay(100);
  }
  Serial.println("CAN initialized");

   pitchYaw.attach(PITCHYAW_PIN, 900, 2100); //PWM pulse high time min/max = 900us-2100us
   wristRotate.attach(WRISTROTATE_PIN, 900, 2100);
   claw.attach(CLAW_PIN, 900, 2100);

   pitchYaw.write(pitchYawSpeed);
   claw.write(clawSpeed);
}

// void MCP2515_ISR() {
//   flagReceive = 1;
// }


void loop() {
  // continuously wait for CAN msgs.
  // if(flagReceive) {
  //   flagReceive = 0;

    // if CAN msgs are available, read them
      while (CAN_MSGAVAIL == CAN.checkReceive()) { 
         // read data, len: data length, buf: data buf
         Serial.println("checkReceive");
         CAN.readMsgBuf(&len, buff); // reads the CAN msg and stores it in buf

        for(int i=0; i<len; ++i) {
          Serial.print(buff[i]);
          Serial.print(' ');
        }
        Serial.println();
         // update motors
          if (buff[0] == 0x01) { // first byte in msg is the ID. lowerArm ID = 0x01
            updateMotors();
          }
      }
 // }

   //monitor motor position after writing using PID.
   //  once movement has stopped, we want motors to stay in place when force is applied
   if (pitchYawSpeed == 90) {
     if (!pitchYawPIDActive) {
       // Start PID using the stopped encoder position as the input value and set point
       pitchYawPID.Start(pitchYawEncoder.read(), 90, pitchYawEncoder.read()); // input, current value, set point
       pitchYawPIDActive = true;
     }
     
     // get the PID outputs
     const double pitchYawSpeedOutput = pitchYawPID.Run(pitchYawEncoder.read()); // run PID continuously based on encoder input
     pitchYaw.write(pitchYawSpeedOutput);
   }
   else if (pitchYawPID) { // if arm is moving, turn pid off.
     pitchYawPID = false;
   }
   
   if (clawSpeed == 90) {
     if (!clawPIDActive) {
       // Start PID using the stopped encoder position as the input value and set point
       clawPID.Start(clawEncoder.read(), 0, clawEncoder.read());
       clawPIDActive = true;
     }
     
     // get the PID outputs
     const double clawSpeedOutput = clawPID.Run(clawEncoder.read());
     claw.write(clawSpeedOutput);
   }
   else if (clawPIDActive) { // if arm is moving, turn pid off.
     clawPIDActive = false;
   }

}
