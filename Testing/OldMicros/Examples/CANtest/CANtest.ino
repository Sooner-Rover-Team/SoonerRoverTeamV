/*
 * CAN is a way to communicate data over long distances - usually ment for noisy environments like the rover, in a car or in space.
 *   A CAN message consists of an ID to determine who the message is for, and an array of data. Each CAN tranceiver must read the data at
 *   the same speed in order for both ends to make sense of the data. We use 100k bits/second but that's on the lower end.
 */
//-----------------------------------------------------------------

#ifndef __IMXRT1062__
  #error "This sketch should be compiled for Teensy 4.x"
#endif

//-----------------------------------------------------------------
#include <ACAN_T4.h>
//-----------------------------------------------------------------
CANMessage message;
//-----------------------------------------------------------------

void setup () {
  // Setup CAN/ Serial
  pinMode (LED_BUILTIN, OUTPUT) ;
  Serial.begin (115200) ;
  while (!Serial) { // wait for Arduino to connect to Serial Monitor
    delay (50) ;
    digitalWrite (LED_BUILTIN, !digitalRead (LED_BUILTIN)) ;
  }
  ACAN_T4_Settings settings (100 * 1000) ; // 100 kbit/s - must agree on both ends of CAN Bus

  const uint32_t errorCode = ACAN_T4::can3.begin (settings) ;

  if (0 == errorCode) { // print an error code that can be looked up online to source the problem
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
}

void doStuffWithCANMessage(CANMessage message) {
  // read data and either assign it to variables to be used else where or do something immediately with them like write to motors
}


void loop () {
  if (ACAN_T4::can3.receive (message)) { // receive new message and print it
    Serial.print("ID=");
    Serial.print(message.id);
    Serial.print(" msg = ");
    for(int i=0; i<message.len; ++i) {
      Serial.print(message.data[i]);
      Serial.print(", ");
    }
    Serial.println();

    doStuffWithCANMessage(message); // whatever you want to do with the data
  }
}