/*
 * The lower Arm Teensy 4.1 sits in the arm Ebox and is responsible for controlling the base motor and 
 *  the two linear actuators (bicep/forearm). The actuators act like servos (PWM control),
 *  while the base will be controlled with the TALON SRX motor controller, which accepts PWM.
 */
//-----------------------------------------------------------------

#ifndef __IMXRT1062__
  #error "This sketch should be compiled for Teensy 4.x"
#endif

//-----------------------------------------------------------------
#include <ACAN_T4.h>
#include <Servo.h>
// when set to 0, Teensy does not compile anything within the #if DEBUG statements, meaning
//   the Teensy does not have to spend time printing to Serial and also saves memory space
#define DEBUG 0 

#define BICEP_PIN 3
#define FOREARM_PIN 5
#define BASE_PIN 4
#define CAN_LED_PIN 2
#define STOP 1500
//-----------------------------------------------------------------

Servo base, bicep, forearm;

// global speed variables (this step may not be necessary but could help with trouble shooting at some point)
int baseSpeed = 90;
int bicepPosition = 135;
int forearmPosition = 119;

long int timeOut = 0; // used to track time between CAN msgs
CANMessage message;

void setup () {
  // CAN SETUP
  #if DEBUG
  pinMode (LED_BUILTIN, OUTPUT) ;
    Serial.begin (9600) ;
    while (!Serial) { // blink LED if Serial can't open
      delay (50) ;
      digitalWrite (LED_BUILTIN, !digitalRead (LED_BUILTIN)) ;
    }
    Serial.println ("CAN3 loopback test") ;
  #endif

  ACAN_T4_Settings settings (100 * 1000) ; // 100 kbit/s - must agree on both sides of CAN
  const uint32_t errorCode = ACAN_T4::can3.begin (settings) ; // using CAN3 on Teensy

  if (0 == errorCode) {
    #if DEBUG
      Serial.println ("can3 initialized") ;
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

  // Initialize Servo objects to generate PWM signals
  pinMode(CAN_LED_PIN, OUTPUT); // CAN status LED
  base.attach(BASE_PIN, 1000, 2000); // PWM min/max pulse duration = 900us - 2100us
  bicep.attach(BICEP_PIN, 1000, 2000);
  forearm.attach(FOREARM_PIN, 1000, 2000);

  // initial speed/position of motors
  base.write(90);
  bicep.write(135); // inverse kinematics starts arm in this position right now
  forearm.write(119);
}

void updateMotors(CANMessage message) {
  // frame.data should contain values to write to each motor
  #if DEBUG
    Serial.println("Writing to motors");
  #endif
  bicepPosition = message.data[0];
  forearmPosition = message.data[1];
  baseSpeed = message.data[2];

  bicep.write(bicepPosition);
  forearm.write(forearmPosition);
  // map(value, fromMin, fromMax, toMin, toMax) - maps a value from one range to another
  base.write((int)map(baseSpeed, 0, 252, 0, 180)); 
}

void loop () {
  CANMessage message ;

  if (ACAN_T4::can3.receive (message)) {
    digitalWrite(CAN_LED_PIN, HIGH); // status LED to know we are receiving msgs
    #if DEBUG // print what we get
      Serial.print("Message = ");
      for(int i=0; i<message.len; ++i) {
        Serial.print(message.data[i]);
        Serial.print(", ");
      }
      Serial.println();
    #endif
    if((message.id == 0x01) && (message.len == 3)) {
      updateMotors(message);
      timeOut = millis();
    }
    digitalWrite(CAN_LED_PIN, LOW);

    if ((millis() - timeOut) >= 1000) { // if the last good msg recieved was longer than 1 sec ago, stop wheels
      base.write(90);
    }
  }
}
