#include <EtherCard.h>
#include <IPAddress.h>
#include <Servo.h>

// Set equal to 1 for serial debugging
#define DEBUG_MODE 0

// 2 is the drill ID
#define DEVICE_ID 2

// Note: analogWrite() can not be used on pins 9 or 10 because of the servo library.
// Servos can still be used on those pins though
#define PIN_ACTUATOR_UP 5
#define PIN_ACTUATOR_DOWN 3
#define PIN_TALON_FAN 7
#define PIN_TALON_DRILL 6

// servo objects for talon motor controllers
Servo talonFan, talonDrill;

// ethernet interface ip address (static ip)
static byte myip[] = { 10, 0, 0, 103 };
static int myport = 1003;
// gateway ip address
static byte gwip[] = { 10, 0, 0, 1 };
// ethernet mac address - must be unique on your network
static byte mymac[] = { 0xAC, 0xDC, 0x0D, 0xAD, 0x00, 0x00 };
// tcp/ip send and receive buffer
byte Ethernet::buffer[500];

// raw bytes to store from ethernet data
// they are converted to output ranges in updateServos()
char myHash = 0;
char serialHash = 0;
char actuatorDir = 2; // 0 is down, 1 is up, 2 is neither (not moving)
char actuatorSpeed = 0;
char drillSpeed = 0;
char fanSpeed = 0;

unsigned long timeOut = 0;

//callback that prints received packets to the serial port
void udpSerialPrint(uint16_t dest_port, uint8_t src_ip[IP_LEN], uint16_t src_port, const char *data, uint16_t len) {
  IPAddress src(src_ip[0], src_ip[1], src_ip[2], src_ip[3]);

  // serial transmission blueprints:
  
  // drill
  
  // [start transmission = -127 or 255] [2] ...
  // ...[direction (0, 1, or 2)] [actuator speed (-127 to 126)]...
  // ...[drill speed] [fan speed] [hash]
  
  // hash = (sum of data bytes--no start or id) / (num of bytes)

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
    
    if (data[1] == DEVICE_ID)
    {
      if (len != 7)
      {
        #if DEBUG_MODE == 1
        Serial.println("Drill message is wrong length!");
        #endif
        return;
      }
      actuatorDir = data[2];
      actuatorSpeed = data[3];
      drillSpeed = data[4];
      fanSpeed = data[5];
    
      serialHash = data[6];
      myHash = (actuatorDir+actuatorSpeed+drillSpeed+fanSpeed)/4;
      if (myHash == serialHash)
      {
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

  //register udpSerialPrint() to port
  ether.udpServerListenOnPort(&udpSerialPrint, myport);

  // setup servos (they're really Talon motor controllers)
  talonFan.attach(PIN_TALON_FAN);
  talonDrill.attach(PIN_TALON_DRILL);

  talonFan.write(90);
  talonDrill.write(90);

  // Setup actuator control pins (analog outputs)
  pinMode(PIN_ACTUATOR_UP, OUTPUT);
  pinMode(PIN_ACTUATOR_DOWN, OUTPUT);
  
  analogWrite(PIN_ACTUATOR_UP, 0);
  analogWrite(PIN_ACTUATOR_DOWN, 0);
}

void loop() {
  // this must be called for ethercard functions to work.
  ether.packetLoop(ether.packetReceive());

  // stop all motors after 1 second of no messages
  if (millis()-timeOut >= 1000)
  {
    timeOut = millis();
    talonFan.write(90);
    talonDrill.write(90);
    analogWrite(PIN_ACTUATOR_UP, 0);
    analogWrite(PIN_ACTUATOR_DOWN, 0);

#if DEBUG_MODE == 1
    Serial.println("Stopped motors");
#endif
  }
}

void updateServos() {
  // convert char (-127 to 126) to pwm values (0 to 255)
  int speedOutput = actuatorSpeed;
  if (speedOutput < 0)
    speedOutput *= -1;

  speedOutput = map(speedOutput, 0, 90, 0, 255);
  
  if (actuatorSpeed < 0)
  {
    // down
    analogWrite(PIN_ACTUATOR_UP, 0);
    analogWrite(PIN_ACTUATOR_DOWN, speedOutput);
  }
  else if (actuatorSpeed > 0)
  {
    //up
    analogWrite(PIN_ACTUATOR_UP, speedOutput);
    analogWrite(PIN_ACTUATOR_DOWN, 0);
  }
  else
  {
    // not moving
    analogWrite(PIN_ACTUATOR_UP, 0);
    analogWrite(PIN_ACTUATOR_DOWN, 0);
  }

  talonFan.write(map(fanSpeed, -127, 126, 0, 180));
  talonDrill.write(map(drillSpeed, -127, 126, 0, 180));
}
