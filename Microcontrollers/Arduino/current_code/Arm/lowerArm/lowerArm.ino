#include <Servo.h>
#include <SPI.h>
#include <ACAN2515.h>
/*
 * The lower Arm arduino sits in the arm Ebox and is responsible for controlling the base motor and 
 *  the two linear actuators (bicep/forearm). The actuators act like servos
 *  while the base will be controlled with the SPARKMAX motor controller, which accepts PWM.
 */
 #define DEBUG 0

Servo base, bicep, forearm;

#define BICEP_PIN 5
#define FOREARM_PIN 6
#define BASE_PIN 9
#define CAN_LED_PIN A7
#define STOP 1500

 // update variables (this step may not be necessary but could help with trouble shooting at some point)
int baseSpeed = 90;
int bicepPosition = 135;
int forearmPosition = 119;

// CAN Setup
static const byte MCP2515_CS = 10; // clock select pin
static const byte MCP2515_INT = 2; // interupt pin
//ACAN2515 can(MCP2515_CS, SPI, MCP2515_INT);
ACAN2515 can(MCP2515_CS, SPI, 255); // no interrupts
static const uint32_t QUARTZ_FREQUENCY = 8UL * 1000UL * 1000UL; // 8 MHz crystral
CANMessage frame; // the object that will store the CAN data/ID

long int timeOut = 0;


void setup() {
  #if DEBUG
    Serial.begin(9600);
  #endif
  
  // setup for CAN
  SPI.begin();
  ACAN2515Settings settings(QUARTZ_FREQUENCY, 100UL * 1000UL); // 100 kb/s
  settings.mRequestedMode = ACAN2515Settings::NormalMode;
  //const uint16_t errorCode = can.begin(settings, [] { can.isr(); });
  const uint16_t errorCode = can.begin(settings, NULL) ; // Second argument is NULL -> no interrupt service routine
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

  // NANO PWM pins: D3, D5, D6, D9, D10, D11
  pinMode(CAN_LED_PIN, OUTPUT); // CAN status LED
  base.attach(BASE_PIN); // PWM min/max pulse duration = 900us - 2100us
  bicep.attach(BICEP_PIN, 900, 2100);
  forearm.attach(FOREARM_PIN, 900, 2100);

  // initial speed/position of motors
  base.writeMicroseconds(STOP);
  bicep.write(135); // inverse kinematics starts arm in this position right now
  forearm.write(119);
}

void updateMotors() {
  // frame.data should contain values to write to each motor
  bicep.write(frame.data[0]);
  forearm.write(frame.data[1]);
  base.writeMicroseconds((int)map(frame.data[2], 0, 252, 1000, 2000)); 
}

void loop() {
  // CAN RX = [bicepPosition, forearmPosition, baseSpeed], frame.id=0x01
  if (can.available()) { // if a msg is ready to be received
    digitalWrite(CAN_LED_PIN, HIGH); // status LED to know we are receiving msgs
    can.receive(frame); // fill frame with CAN msg
    #if DEBUG // print what we get
      if(frame.id == 0x01) {
        //Serial.print("ID = ");
      // Serial.println(frame.id);
        //Serial.print("Length = ");
        //Serial.println(frame.len);
        for(int i=0; i<frame.len; ++i) {
          Serial.print(frame.data[i]);
          Serial.print(", ");
        }
        Serial.println();
      }
    #endif
    if(frame.id == 0x01) { // lowerarm ID = 0x01
      if(frame.len == 3) { // one byte for each motor
        updateMotors();
        timeOut = millis();
      }
    }
    digitalWrite(CAN_LED_PIN, LOW);  

    if ((millis() - timeOut) >= 1000) { // if the last good msg recieved was longer than 1 sec ago, stop wheels
      base.writeMicroseconds(STOP);
    }
  }
  delay(10);
}
