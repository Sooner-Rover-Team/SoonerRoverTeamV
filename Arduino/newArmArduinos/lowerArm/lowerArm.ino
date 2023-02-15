#include <Servo.h>
#include <SPI.h>
#include <mcp2515_can.h>
/*
 * The lower Arm arduino sits in the arm Ebox and is responsible for controlling the base motor and 
 *  the two linear actuators (bicep/forearm). The actuators act like servos
 *  while the base will be controlled with the SPARKMAX motor controller, which accepts PWM.
 */

Servo base, bicep, forearm;

#define BASE_PIN 5
#define WRIST_PIN 6
#define BICEP_PIN 9
#define FOREARM_PIN 10
#define CAN_RX_LED 1

 // update variables (this step may not be necessary but could help with trouble shooting at some point)
int baseSpeed = 90;
int bicepPosition = 180;
int forearmPosition = 180;

// CAN RX buf = [0x01, bicepPosition, forearmPosition, baseSpeed, checksum]
const int SPI_CS_PIN = 10;
const int CAN_INT_PIN = 2;
mcp2515_can CAN(SPI_CS_PIN);
unsigned char flagReceive = 0;
unsigned char len = 5;
unsigned char buf[len];
char str[20];

void setup() {
  // setup for CAN
  //attachInterrupt(digitalPinToInterrupt(CAN_INT_PIN), MCP2515_ISR, FALLING);
  // initialize can bus with 500kHz baudrate
  while (CAN_OK != CAN.begin(CAN_500KBPS)) {
    Serial.println("CAN init fail, retry...");
    delay(100);
  }
  Serial.println("CAN initialized");


  // not sure of which microcontroller right now. I vote arduino nano (only cuz I've used it a lot)
  // NANO PWM pins: D3, D5, D6, D9, D10, D11
  base.attach(BASE_PIN, 900, 2100); // PWM min/max pulse duration = 900us - 2100us
  bicep.attach(BICEP_PIN, 900, 2100);
  forearm.attach(FOREARM_PIN, 900, 2100);

  // initial speed/position of motors
  base.write(baseSpeed);
  bicep.write(bicepPosition);
  forearm.write(forearmPosition);
}

void MCP2515_ISR() {
  flagReceive = 1;
}

void updateMotors() {
  // buf should contain servo values to write to each motor
  base.write(map(buf[1], 0, 255, 0, 180));
  bicep.write(buf[2]);
  forearm.write(buf[3]);
}

void loop() {
  // continuously wait for CAN msgs.
  if(flagReceive) {
    flagReceive = 0;

    // if CAN msgs are available, read them
      while (CAN_MSGAVAIL == CAN.checkReceive()) { 
         // read data, len: data length, buf: data buf
         Serial.println("checkReceive");
         CAN.readMsgBuf(&len, buf); // reads the CAN msg and stores it in buf
         // update motors
         if (buf[0] == 0x01) { // first byte in msg is the ID = 0x01
          updateMotors();
         }
      }
  }
}
