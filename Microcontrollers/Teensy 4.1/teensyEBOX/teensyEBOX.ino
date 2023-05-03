/*
    THIS TEENSY RECEIVES UDP MESSAGES FROM ROUTER AND SENDS
      CAN MESSAGES TO OTHER MICROCONTROLLERS ON ROVER. IT IS
      ALSO RESPONSIBLE FOR CONTROLLING WHEELS FOR NOW

     Pin wiring diagram

     [],pin  front   [],pin
     0,6     0-|-0    3,3
               |
     1,7     0-|-0   -4,4
               |
    -2,8     0-|-0   -5,5
     "-" indicaes wheel's polarity needs to be reversed

     gimbal pan: 
     gimbal tilt: 

     LED pins RGB: 11,10,12

     Pins used by Ethernet:

     Wheel UDP message:
     [0x01, 0x01, wheel0, wheel1, wheel2, wheel3, wheel4, wheel5, wheel6, checkSum]

     LED UDP message:
     [0x01, 0x02, redLED, greenLED, blueLED]

     ARM UDP Message:
     [0x02, bicep, forearm, base, pitch, roll, claw]

     SCIENCE UDP Message:
     [0x03, actuator, carousel, fan, microscope]
*/

#ifndef __IMXRT1062__
  #error "This sketch should be compiled for Teensy 4.x"
#endif

#include <NativeEthernet.h> // NativeEthernet.h and NativeEthernetUDP.h are the exact same as the arduino Ethernet.h and EtherbetUDP.h.
#include <NativeEthernetUdp.h>
#include <ACAN_T4.h>
#include <Servo.h>

// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network:
byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
IPAddress ip(10, 0, 0, 101);

unsigned int localPort = 1001; // local port to listen on

// buffers for receiving and sending data
unsigned char packetBuffer[UDP_TX_PACKET_MAX_SIZE];  // buffer to hold incoming packet,
char ReplyBuffer[] = "acknowledged";        // a string to send back

// An EthernetUDP instance to let us send and receive packets over UDP
EthernetUDP Udp;

// The current CAN message to be sent out
CANMessage message;

#define DEBUG 0 // set to 0 to avoid compiling print statements (will save space, don't need to print if running on rover)

#define WHEEL 0x01 // UDP IDs
#define ARM 0x02
#define SCIENCE 0x03
#define LED 0x02
#define LOWER_ARM 0x01 // CAN IDs
#define UPPER_ARM 0x02
#define CAN_LED 2
#define UDP_LED 1
#define greenPin 10 // LED pins on Teensy
#define redPin 11
#define bluePin 12

int checkSum = 0; // used to check for errors in recieved message.

int vertPos = 90; // position of gimbal
int horizPos = 90; 

Servo wheel0, wheel1, wheel2, wheel3, wheel4, wheel5, gimbalVert, gimbalHoriz;
Servo wheels[6] = {wheel0, wheel1, wheel2, wheel3, wheel4, wheel5};
// if some connections are reversed, wheel0.write(0) may not be the same direction as wheel1.write(0)
bool wheelReverse[6] = {true, false, false, true, false, true};

unsigned long timeOut = 0; // used to measure time between msgs. If we go a full second without new msgs, stop wheels so rover doesn't run away from us

// super awesome fun proportional wheel control variables
int targetSpeeds[6] = {126, 126, 126, 126, 126, 126}; // neutral
double currentSpeeds[6] = {126, 126, 126, 126, 126, 126};
bool proportionalControl = false;
unsigned long lastLoop = 0; // milli time of last loop
double deltaLoop = 0.0; // seconds since last loop
double Kp = 3.5; // proportional change between target and current
double Kp_thresh = 0.4; // % of wheel speed to apply proportional control under

double error[6];

// define time in microseconds of width of pulse
const int PWM_LOW = 1000;
const int PWM_HIGH = 2000;
const int PWM_NEUTRAL = 1500; 

void setup() {
  // Open serial communications and wait for port to open:
  pinMode(LED_BUILTIN, OUTPUT);
  #if DEBUG
    Serial.begin(115200);
    delay(100);
    Serial.println("Starting");
  #endif
  // while (!Serial) {
  //   delay (50);
  //   digitalWrite (LED_BUILTIN, !digitalRead (LED_BUILTIN)); // wait for serial port to connect. Needed for native USB port only
  // }
  // You can use Ethernet.init(pin) to configure the CS pin
  //Ethernet.init(10);  // Most Arduino shields <---
  //Ethernet.init(5);   // MKR ETH Shield
  //Ethernet.init(0);   // Teensy 2.0
  //Ethernet.init(20);  // Teensy++ 2.0
  //Ethernet.init(15);  // ESP8266 with Adafruit FeatherWing Ethernet
  //Ethernet.init(33);  // ESP32 with Adafruit FeatherWing Ethernet
  wheel0.attach(6, 1000, 2000);
  wheel1.attach(7, 1000, 2000);
  wheel2.attach(8, 1000, 2000);
  wheel3.attach(3, 1000, 2000);
  wheel4.attach(4, 1000, 2000);
  wheel5.attach(5, 1000, 2000);

  wheel0.write(90);
  delay(5);
  wheel1.write(90);
  delay(5);
  wheel2.write(90);
  delay(5);
  wheel3.write(90);
  delay(5);
  wheel4.write(90);
  delay(5);
  wheel5.write(90);

  // gimbalVert.attach(10);
  // gimbalHoriz.attach(11));

  pinMode(redPin, OUTPUT); // red
  pinMode(greenPin, OUTPUT); // green
  pinMode(bluePin, OUTPUT); // blue
  pinMode(CAN_LED, OUTPUT);
  // start the Ethernet
  Ethernet.begin(mac, ip);
  #if DEBUG
    Serial.println("Starting ethernet");
  #endif
  // Check for Ethernet hardware present
  if (Ethernet.hardwareStatus() == EthernetNoHardware) {
    #if DEBUG
      Serial.println("Ethernet shield was not found.  Sorry, can't run without hardware. :(");
    #endif
    while (true) {
      delay(1); // do nothing, no point running without Ethernet hardware
    }
  }
  if (Ethernet.linkStatus() == LinkOFF) {
    #if DEBUG
      Serial.println("Ethernet cable is not connected.");
    #endif
  }
  // initialize the CAN settings and start
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

  // start UDP
  Udp.begin(localPort);
}

void printCanMsg(CANMessage &frame){
    //Serial.print ("  id: ");Serial.println (frame.id,HEX);
    //Serial.print ("  len: ");Serial.println (frame.len);
    //Serial.print ("  data: ");
    for(int x=0;x<frame.len;x++) {
      Serial.print (frame.data[x]); Serial.print(":");
    }
    Serial.println ("");
}

// clips a value so it stays in range [low, high]
double clip(double value, double low, double high) {
  if (value < low) value = low;
  if (value > high) value = high;
  return value;
}

void updateGimbal(int vertical, int horizontal) {
  // inputs are 0 for counter-clockwise, 1 for nothing, 2 for clockwise
   switch(vertical){
      case 2: 
        if(vertPos >= 180){
          vertPos=179;
        }
        vertPos += 1; 
        break;
      case 0:
        if(vertPos <= 0){
          vertPos=1;
        }
        vertPos -= 1; 
        break;
   }
    switch(horizontal) {
      case 2: 
        if(horizPos >= 180){
          horizPos=179;
        }
        horizPos += 1; 
        break;
      case 0:
        if(horizPos <= 0){
          horizPos=1;
        }
        horizPos -= 1; 
        break;
      }
  gimbalVert.write(vertPos);
  gimbalHoriz.write(horizPos);
}

//LED msg: [0x01, 0x02, red, green, blue]
//WHEEL msg: [0x01, 0x01, w1, w2, w3, w4, w5, w6, checkSum]
void updateWheels(unsigned char msg[], int msgSize) {
  checkSum = 0;
  #if DEBUG
    //Serial.println("msg recieved:");
    for(int i=0; i<msgSize; ++i) {
      Serial.print(uint8_t(msg[i]));
      Serial.print(", ");
    }
    Serial.println();
  #endif

  /**************LED MSG *****************/
  if (msg[1] == LED) {
    if(msgSize == 5) {
      if(uint8_t(msg[2]) > 0) {
        digitalWrite(redPin, HIGH);
        Serial.println("RED HIGH");
      }
      else {
        digitalWrite(redPin, LOW);
      }
      if(uint8_t(msg[3]) > 0) {
        digitalWrite(greenPin, HIGH);
      }
      else {
        digitalWrite(greenPin, LOW);
      }
      if(uint8_t(msg[4]) > 0) {
        digitalWrite(bluePin, HIGH);
      }
      else {
        digitalWrite(bluePin, LOW);
      }
    } 
    else {
      #if DEBUG
        Serial.println("msg for LEDS was wrong length... ignoring this message.");
      #endif
    }
  }  
  /**************WHEEL MSG *****************/
  else if (msg[1] == WHEEL) {
    if(msgSize == 9) {
      for(int i=2; i<8; i++) { 
        checkSum += msg[i];
      }
      checkSum = checkSum & 0xff;
      #if DEBUG // commented because its hard to read other print statements, keep in case its needed
        // Serial.print("Calcuated checksum: ");
        // Serial.println(checkSum);
        // Serial.print("Received checksum: ");
        // Serial.println((int)msg[8]);
      #endif
      if(checkSum == uint8_t(msg[8])) {
        timeOut = millis(); // save time so we know how long it's been between this and next msg
        // set the appropriate target speeds
        for (int i = 0; i < 6; i++) {
          targetSpeeds[i] = (uint8_t)msg[i+2];
        }
        for (int i = 0; i < 6; i++) {
          if (wheelReverse[i]) {
          wheels[i].write((int)map(targetSpeeds[i], 252, 0, 0, 180)); 
          Serial.print((int)map(currentSpeeds[i], 252, 0, 0, 180));
          Serial.print(", ");       
          } else {
            wheels[i].write((int)map(targetSpeeds[i], 0, 252, 0, 180));
        }
    }          
        //updateGimbal(uint8_t(msg[8]), uint8_t(msg[9])); // NOT IMPLEMENTED RIGHT NOW
      }
      else {
        #if DEBUG
          Serial.println("checkSum for WHEELS was incorrect... ignoring this message.");
        #endif
      }
    }
    else {
      #if DEBUG
        Serial.println("msg for WHEELS was wrong length... ignoring this message.");
      #endif
    }
  }
  else {
    #if DEBUG
      Serial.println("msg was for the wrong device... ignoring this message.");
    #endif
  }
}

void sendArmCAN(unsigned char msg[], int msgSize) {
  if(msgSize == 8) {
    checkSum = 0;
    for(int i=1; i<7; i++) { 
        checkSum += msg[i];
    }
    checkSum = checkSum & 0xff;
    if(checkSum == uint8_t(msg[7])) {
      message.id = LOWER_ARM; // ID for lower arm
      message.len = 3;
      memcpy(message.data, &msg[1], 3); // base, bicep, forearm
     // printCanMsg(message);
      bool ok = ACAN_T4::can3.tryToSend (message) ;
      if(ok && DEBUG) {
        Serial.println("lower sent"); 
      }
      message.id = UPPER_ARM;
      message.len = 3;
      memcpy(message.data, &msg[4], 3); // pitch, roll, claw
      //printCanMsg(message);
      ok = ACAN_T4::can3.tryToSend (message) ;
      if(ok && DEBUG) {
        Serial.println("upper sent"); 
      }
    }
    else {
      #if DEBUG
        Serial.println("checkSum for ARM was incorrect... ignoring this message.");
      #endif
    }
  }
  else {
    #if DEBUG
        Serial.println("checkSum for ARM was incorrect... ignoring this message.");
      #endif
  }
}

void sendScienceCAN(unsigned char msg[], int msgSize) {
  if(msgSize == 6) {
    checkSum = 0;
    for(int i=1; i<5; i++) { 
        checkSum += msg[i];
    }
    checkSum = checkSum & 0xff;
    if(checkSum == uint8_t(msg[5])) {
      message.id = SCIENCE; // ID for lower arm
      message.len = 4;
      memcpy(message.data, &msg[1], 4); // actuator, carousel, fan, microscope
      bool ok = ACAN_T4::can1.tryToSend (message) ;
      if(ok) {
        #if DEBUG
          Serial.print("Science sent, ");
        #endif   
      }
    }
    else {
      #if DEBUG
        Serial.println("checkSum for SCIENCE was incorrect... ignoring this message.");
      #endif
    }
  }
  else {
    #if DEBUG
        Serial.println("checkSum for SCIENCE was incorrect... ignoring this message.");
      #endif
  }
}

void loop() {
  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    digitalWrite(CAN_LED, HIGH);
    #if DEBUG
      // Serial.print("Received packet of size ");
      // Serial.println(packetSize);
      // Serial.print("From ");
      // IPAddress remote = Udp.remoteIP();
      // for (int i=0; i < 4; i++) {
      //   Serial.print(remote[i], DEC);
      //   if (i < 3) {
      //     Serial.print(".");
      //   }
      // }
      // Serial.print(", port ");
      // Serial.println(Udp.remotePort());
    #endif
    // read the packet into packetBuffer
    Udp.read(packetBuffer, packetSize);
    #if DEBUG
      for(int i=0; i<packetSize; ++i) {
        Serial.print(packetBuffer[i]);
        Serial.print(", ");
      }
      Serial.println();
    #endif
    // timeOut = millis();
    if(packetBuffer[0] == WHEEL) { // means the UDP message was for the wheel system
      updateWheels(packetBuffer, packetSize);
    }
    else if(packetBuffer[0] == ARM) {
      sendArmCAN(packetBuffer, packetSize);
    }
    else if(packetBuffer[0] == SCIENCE) {
      sendScienceCAN(packetBuffer, packetSize);
    }
    else {
      #if DEBUG
        Serial.println("ID unrecognized");
      #endif
    }
    // send a reply to the IP address and port that sent us the packet we received (NEVER TRIED THIS)
    //Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    //Udp.write(ReplyBuffer);
    //Udp.endPacket();
    digitalWrite(CAN_LED, LOW);
  }
  if ( millis() - timeOut >= 1000) // if the last good msg recieved was longer than 1 sec ago, stop wheels
  {
    timeOut = millis();
    // for (int i = 0; i < 6; i++) {
    //   wheels[i].write(90);
    //   delay(5);
    //   currentSpeeds[i] = 126;
    //   targetSpeeds[i] = 126;
    // }
    wheel0.write(90);
    wheel1.write(90);
    wheel2.write(90);
    wheel3.write(90);
    wheel4.write(90);
    wheel5.write(90);
    // gimbalVert.write(90);
    // gimbalHoriz.write(90);

    #if DEBUG
    Serial.println("Stopped motors");
    #endif
  } else {
    deltaLoop = (millis() - lastLoop)/1000.0;
    for (int i = 0; i < 6; i++) {
      // if using proportional control, look at the difference between the current and desired speed
      if (proportionalControl && abs(currentSpeeds[i] - 126) < (126*Kp_thresh)) {
      // if (proportionalControl) {
        error[i] = targetSpeeds[i] - currentSpeeds[i];
        double output = error[i]*Kp*deltaLoop;
        currentSpeeds[i] += output; 
      } else {
        currentSpeeds[i] = targetSpeeds[i];
      }
      // if the target is to stop, set the current to that as well
      if (targetSpeeds[i] == 126) currentSpeeds[i] = 126;
      // also clip the current speed value just to be safe
      currentSpeeds[i] = clip(currentSpeeds[i], 0, 252);

      // if (i == 0) {
      //   Serial.println(currentSpeeds[i]);
      // }


      // if (wheelReverse[i]) {
      //   wheels[i].write((int)map(currentSpeeds[i], 252, 0, 0, 180)); 
      //   Serial.print((int)map(currentSpeeds[i], 252, 0, 0, 180));
      //   Serial.print(", ");       
      // } else {
      //   wheels[i].write((int)map(currentSpeeds[i], 0, 252, 0, 180));
      //   Serial.print((int)map(currentSpeeds[i], 0, 252, 0, 180));
      //   Serial.print(", "); 
      // }

      // wheels[0].write((int)map(currentSpeeds[0], 252, 0, 0, 180));
      // wheel0.write((int)map(currentSpeeds[0], 252, 0, 0, 180));
      // wheel1.write((int)map(currentSpeeds[1], 0, 252, 0, 180));
      // wheel2.write((int)map(currentSpeeds[2], 0, 252, 0, 180));
      // wheel3.write((int)map(currentSpeeds[3], 252, 0, 0, 180));
      // wheel4.write((int)map(currentSpeeds[4], 0, 252, 0, 180));
      // wheel5.write((int)map(currentSpeeds[5], 252, 0, 0, 180));
    }
    // for (int i = 0; i < 6; i++) {
    //   if (wheelReverse[i]) {
    //     wheels[i].write((int)map(targetSpeeds[i], 252, 0, 0, 180)); 
    //     // Serial.print((int)map(currentSpeeds[i], 252, 0, 0, 180));
    //     // Serial.print(", ");       
    //   } else {
    //     wheels[i].write((int)map(targetSpeeds[i], 0, 252, 0, 180));
    //   }
    // }
    //bool wheelReverse[6] = {true, false, false, true, false, true};

    wheel0.write((int)map(currentSpeeds[0], 252, 0, 0, 180));
    wheel1.write((int)map(currentSpeeds[1], 0, 252, 0, 180));
    wheel2.write((int)map(currentSpeeds[2], 0, 252, 0, 180));
    wheel3.write((int)map(currentSpeeds[3], 252, 0, 0, 180));
    wheel4.write((int)map(currentSpeeds[4], 0, 252, 0, 180));
    wheel5.write((int)map(currentSpeeds[5], 252, 0, 0, 180));
        // Serial.print((int)map(currentSpeeds[i], 0, 252, 0, 180));
        // Serial.print(", ");
      //just debugging stuff
      //if (i == 3) {
        // Serial.println(wheels[0].read());
      //   Serial.print("ts: ");
      //   Serial.print(targetSpeeds[i]);
      //   Serial.print(", cs: ");
        //Serial.println(currentSpeeds[i]);      
      //}

    //Serial.println();
    // remember milli time of the last loop
    lastLoop = millis();
  }
}

