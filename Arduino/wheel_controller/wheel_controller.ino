#include <EtherCard.h>
#include <IPAddress.h>
#include <Servo.h>

//Set equal to 1 for serial debugging
#define DEBUG_MODE 0

/*
     Pin wiring diagram

     [],pin  front   [],pin
     0,2     0-|-0    3,7
               |
     1,3     0-|-0   -4,6
               |
    -2,4     0-|-0   -5,5
     "-" indicaes wheel's polarity needs to be reversed

     gimbal pan: A2
     gimbal tilt: A1
     brake disk: A3

     LED RGB: A5, 9, 8

     ethernet adapter: 10, 11, 12, 13

     jetson power button: A0
*/
// Note: analogWrite() can not be used on pins 9 or 10 because of the servo library.
// Servos can still be used on those pins though
#define WHEEL_FL A4
#define WHEEL_ML 3
#define WHEEL_RL 4

#define WHEEL_FR 7
#define WHEEL_MR 6
#define WHEEL_RR 5

#define SERVO_PAN A2
#define SERVO_TILT A1
#define SERVO_BRAKE A3

#define LED_R 9
#define LED_G A5
#define LED_B 8


#define JETSON_POWER A0

// ethernet interface ip address (static ip)
static byte myip[] = { 10, 0, 0, 101 };
// gateway ip address
static byte gwip[] = { 10, 0, 0, 1 };
// ethernet mac address - must be unique on your network
static byte mymac[] = { 0x70, 0x69, 0xFF, 0xFF, 0x30, 0x31 };
// tcp/ip send and receive buffer
byte Ethernet::buffer[500];

// wheel_controller stuff
Servo wheel[6], gimbal_pan, gimbal_tilt, disk;
char myHash = 0;
char serialHash = 0;
char pan = 0;
char tiltByte = 0;
char leftWheels = 0;
char rightWheels = 0;
char modifiers = 0;
char tilt = 90;

unsigned long timeOut = 0;


//callback that prints received packets to the serial port
void udpSerialPrint(uint16_t dest_port, uint8_t src_ip[IP_LEN], uint16_t src_port, const char *data, uint16_t len) {
  IPAddress src(src_ip[0], src_ip[1], src_ip[2], src_ip[3]);

  // serial transmission blueprints:
  
  // wheels
  // [start transmission = -127 or 255] [0] [overdrive] [left wheels]...
  // ...[right wheels] [gimble tilt] [gimble pan] [hash]
  // hash = (sum of data bytes--no start or id) / (num of bytes)
  // all message bytes will be within the range [-90,90]

  // lights
  // [start transmission = -127] [1] [00000RGB] [hash]

#if DEBUG_MODE == 1
  for (int i = 0; i < len; i++)
  {
    Serial.print(int(data[i]));
    Serial.print(", ");
  }
  Serial.print("\n");
#endif

  // check for -127, message type
  if (len >= 2)
  {
    if (data[0] != -127)
    {
      #if DEBUG_MODE == 1
      Serial.println("Message does not start with -127!");
      #endif
      return;
    }
    
    if (data[1] == 0) // wheel type
    {
      if (len != 8)
      {
        #if DEBUG_MODE == 1
        Serial.println("Wheel message is wrong length!");
        #endif
        return;
      }
    
      modifiers = data[2];
    
      leftWheels = data[3];
    
      rightWheels = data[4];
    
      tiltByte = data[5];
      tilt += tiltByte;
      if (tilt < 40 || tilt >= 127)
        tilt -= tiltByte;
    
      pan = data[6];
    
      serialHash = data[7];
      myHash = (pan + tiltByte + leftWheels + rightWheels + modifiers) / 5;
      if (myHash == serialHash)
      {
        //sprintf(serResp, "%d\t%d\t%d\t%d\t%d\t%d", overdrive, leftWheels, rightWheels, tilt, pan, serialHash);
        //Serial.println(serResp);
        updateServos();
        timeOut = millis();
      }
      #if DEBUG_MODE == 1
      else
      {
        Serial.println("Bad hash!");
      }
      #endif
    }
    
    else if(data[1] == 1) // light type
    {
      if (len != 4)
      {
        #if DEBUG_MODE == 1
        Serial.println("Light message is wrong length!");
        #endif
        return;
      }

      if (data[2] != data[3]) // kind of dumb but it follows the same standard as before
      {
        #if DEBUG_MODE == 1
        Serial.println("Bad hash!");
        #endif
        return;
      }

      // red
      if (data[2] & 0x4)
        digitalWrite(LED_R, HIGH);
      else
        digitalWrite(LED_R, LOW);
      // green
      if (data[2] & 0x2)
        digitalWrite(LED_G, HIGH);
      else
        digitalWrite(LED_G, LOW);
      // blue
      if (data[2] & 0x1)
        digitalWrite(LED_B, HIGH);
      else
        digitalWrite(LED_B, LOW);

      #if DEBUG_MODE == 1
      String debug = "Changed LEDs (";
      
      if (data[2] & 0x4)
        debug += "1";
      else
        debug += "0";

      if (data[2] & 0x2)
        debug += "1";
      else
        debug += "0";

      if (data[2] & 0x1)
        debug += "1)";
      else
        debug += "0)";
      
      Serial.println(debug);
      #endif
    }

    else // unknown type
    {
      #if DEBUG_MODE == 1
      Serial.println("Unknown device id!");
      #endif
      return;
    }
  }
}

void setup() {
#if DEBUG_MODE == 1
  Serial.begin(9600);
  if (ether.begin(sizeof Ethernet::buffer, mymac, 10) == 0)
    Serial.println(F("Failed to access Ethernet controller"));
#else
  ether.begin(sizeof Ethernet::buffer, mymac, 10);
#endif

  ether.staticSetup(myip, gwip);

  ether.printIp("IP:  ", ether.myip);
  ether.printIp("GW:  ", ether.gwip);
  ether.printIp("DNS: ", ether.dnsip);

  //register udpSerialPrint() to port 1337
  ether.udpServerListenOnPort(&udpSerialPrint, 1001);

  // setup servos
  wheel[0].attach(WHEEL_FL);
  wheel[1].attach(WHEEL_ML);
  wheel[2].attach(WHEEL_RL);
  wheel[3].attach(WHEEL_FR);
  wheel[4].attach(WHEEL_MR);
  wheel[5].attach(WHEEL_RR);
  gimbal_pan.attach(SERVO_PAN);
  gimbal_tilt.attach(SERVO_TILT);
  disk.attach(SERVO_BRAKE);

  wheel[0].write(90);
  wheel[1].write(90);
  wheel[2].write(90);
  wheel[3].write(90);
  wheel[4].write(90);
  wheel[5].write(90);
  gimbal_pan.write(90);
  gimbal_tilt.write(90);
  disk.write(90);

  // Setup LED pins
  pinMode(LED_R, OUTPUT);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_B, OUTPUT);
  
  digitalWrite(LED_R, LOW);
  digitalWrite(LED_G, LOW);
  digitalWrite(LED_B, LOW);
  
  // Press jeston's power button (Currently unconnected)
  pinMode(JETSON_POWER, OUTPUT);
  delay(5000);
  digitalWrite(JETSON_POWER, HIGH);
  delay(2000);
  digitalWrite(JETSON_POWER, LOW);
}

void loop() {
  // this must be called for ethercard functions to work.
  ether.packetLoop(ether.packetReceive());

  // stop all motors after 1 second of no messages
  if ( millis() - timeOut >= 1000)
  {
    timeOut = millis();
    wheel[0].write(90);
    wheel[1].write(90);
    wheel[2].write(90);
    wheel[3].write(90);
    wheel[4].write(90);
    wheel[5].write(90);
    gimbal_tilt.write(90);
    disk.write(90);

#if DEBUG_MODE == 1
    Serial.println("Stopped motors");
#endif
  }
}

void updateServos() {
  int speeds[6];
  speeds[0] = 90 + (leftWheels * 0.9);
  speeds[1] = 90 + (leftWheels * 0.9);
  speeds[2] = 90 - (leftWheels * 0.9);
  speeds[3] = 90 + (rightWheels * 0.9);
  speeds[4] = 90 - (rightWheels * 0.9);
  speeds[5] = 90 - (rightWheels * 0.9);
  if ((modifiers & 1)) {
    disk.write(180);
  } else {
    disk.write(90);
  }
  if (modifiers & 8) {
    gimbal_pan.write(90);
    gimbal_tilt.write(90);
  } else {
    gimbal_pan.write(93 + pan);
    gimbal_tilt.write(tilt);
  }
  //
  if ((modifiers & 2) && ( modifiers & 4)) {
    wheel[0].write(speeds[0]);
    wheel[3].write(speeds[3]);
    wheel[2].write(90-(speeds[2]-90));
    wheel[5].write(90-(speeds[5]-90));
  }
  //
  if (modifiers & 2) {
    wheel[0].write(speeds[0]);
    wheel[3].write(speeds[3]);
    return;
  }
  // just the front wheels
  if (modifiers & 4) {
    wheel[2].write(speeds[2]);
    wheel[5].write(speeds[5]);
    return;
  } else {
    wheel[0].write(speeds[0]);// * 1/2));
    wheel[1].write(speeds[1]);
    wheel[2].write(speeds[2]);
    wheel[3].write(speeds[3]);
    wheel[4].write(speeds[4]);
    wheel[5].write(speeds[5]);
  }

}
