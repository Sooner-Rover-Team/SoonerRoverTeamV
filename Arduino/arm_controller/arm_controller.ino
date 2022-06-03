#include <EtherCard.h>
#include <IPAddress.h>
#include <Servo.h>

// Set equal to 1 for serial debugging
#define DEBUG_MODE 0

// Note: analogWrite() can not be used on pins 9 or 10 because of the servo library.
// Servos can still be used on those pins though

// The ethernet adapter uses pins 10, 11, 12, and 13

// 3, 5, 6
#define BASE_PIN A0
#define SHOULDER_PIN A1
#define ELBOW_PIN A2
#define CLAW_OPEN 8
#define CLAW_CLOSE 9

#define WRIST_L1_PIN 2
#define WRIST_L2_PIN 3
#define WRIST_L_SPEED_PIN 4

#define WRIST_R1_PIN 7
#define WRIST_R2_PIN 6
#define WRIST_R_SPEED_PIN 5

#define DEVICE_ID 1

// ethernet interface ip address (static ip)
static byte myip[] = {10, 0, 0, 102};
//static byte myip[] = {192, 168, 1, 102};
static int myport = 1002;
// gateway ip address
static byte gwip[] = {10, 0, 0, 1};
//static byte gwip[] = {192, 168, 1, 1};
// ethernet mac address - must be unique on your network
static byte mymac[] = {0x72, 0x69, 0xFF, 0xFF, 0x30, 0x31};
// tcp/ip send and receive buffer
byte Ethernet::buffer[500];

//
unsigned char base_speed = 90;
unsigned char shoulder_pos = 135;
unsigned char elbow_pos = 119;
char wristTheta_speed = 0;
char wristPhi_speed = 0;
int claw_dir = 1;

bool stopped = false;

unsigned char serialHash = 0;
unsigned char myHash = 81;

unsigned long timeOut = 0;

// talon/servo
Servo base, shoulder, elbow;

// callback that prints received packets to the serial port
void udpSerialPrint(uint16_t dest_port, uint8_t src_ip[IP_LEN], uint16_t src_port, const char *data, uint16_t len)
{
  IPAddress src(src_ip[0], src_ip[1], src_ip[2], src_ip[3]);

  // serial transmission blueprints:
  // hash = (sum of data bytes--no start or id) / (num of bytes)

#if DEBUG_MODE == 1
  for (int i = 0; i < len; i++)
  {
    Serial.print(uint8_t(data[i]));
    Serial.print(", ");
  }
  Serial.print("\n");
#endif

  // check for 255, message type
  if (len >= 2)
  {
    if (uint8_t(data[0]) != 255)
    {
#if DEBUG_MODE == 1
      Serial.println("Message does not start with 255!");
#endif
      return;
    }

    if (data[1] == DEVICE_ID)
    {
      if (len != 9)
      {
#if DEBUG_MODE == 1
        Serial.println("Message is wrong length!");
#endif
        return;
      }

      base_speed = uint8_t(data[2]);
      shoulder_pos = uint8_t(data[3]);
      elbow_pos = uint8_t(data[4]);
      wristTheta_speed = uint8_t(data[5]);
      wristPhi_speed = uint8_t(data[6]);
      claw_dir = uint8_t(data[7]);
      serialHash = uint8_t(data[8]);
      myHash = (base_speed + shoulder_pos + elbow_pos + wristTheta_speed + wristPhi_speed + claw_dir) & 0xff;
#if DEBUG_MODE
//      Serial.print("wrist_theta: ");
//      Serial.println(wristTheta_speed);
//      Serial.print("wrist_phi: ");
//      Serial.println(wristPhi_speed);
#endif
      if (myHash == serialHash)
      {
#if DEBUG_MODE
      //  Serial.println("servos updated");
#endif
        updateServos();
        timeOut = millis();
      }
#if DEBUG_MODE == 1
      else
      {
        Serial.print("Bad hash!");
        Serial.println(myHash);
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

void setup()
{
#if DEBUG_MODE == 1
  Serial.begin(9600);
  if (ether.begin(sizeof Ethernet::buffer, mymac, 10) == 0)
    Serial.println(F("Failed to access Ethernet controller"));
#else
  ether.begin(sizeof Ethernet::buffer, mymac, 10);
#endif

  ether.staticSetup(myip, gwip);

  //  ether.printIp("IP:  ", ether.myip);
  //  ether.printIp("GW:  ", ether.gwip);
  //  ether.printIp("DNS: ", ether.dnsip);

  // register udpSerialPrint()
  ether.udpServerListenOnPort(&udpSerialPrint, myport);

  // servo/talon pins
  base.attach(BASE_PIN);
  shoulder.attach(SHOULDER_PIN);
  elbow.attach(ELBOW_PIN);

  base.write(base_speed);
  shoulder.write(shoulder_pos);
  elbow.write(elbow_pos);
  

  // wrist motor pins
  pinMode(WRIST_L1_PIN, OUTPUT);
  pinMode(WRIST_L2_PIN, OUTPUT);
  pinMode(WRIST_L_SPEED_PIN, OUTPUT);
  pinMode(WRIST_R1_PIN, OUTPUT);
  pinMode(WRIST_R2_PIN, OUTPUT);
  pinMode(WRIST_R_SPEED_PIN, OUTPUT);
  pinMode(CLAW_OPEN, OUTPUT);
  pinMode(CLAW_CLOSE, OUTPUT);

  digitalWrite(WRIST_L1_PIN, LOW);
  digitalWrite(WRIST_L2_PIN, LOW);
  analogWrite(WRIST_L_SPEED_PIN, 0);
  digitalWrite(WRIST_R1_PIN, LOW);
  digitalWrite(WRIST_R2_PIN, LOW);
  analogWrite(WRIST_R_SPEED_PIN, 0);
  digitalWrite(CLAW_OPEN, LOW);
  digitalWrite(CLAW_CLOSE, LOW);
}

void loop()
{
  // this must be called for ethercard functions to work.
  ether.packetLoop(ether.packetReceive());
  delay(20);

  // stop all motors after 1 second of no messages
  if (millis() - timeOut >= 1000 && !stopped)
  {
    timeOut = millis();

    base.write(90);
    shoulder.write(shoulder_pos);
    elbow.write(elbow_pos);
    digitalWrite(WRIST_L1_PIN, LOW);
    digitalWrite(WRIST_L2_PIN, LOW);
    analogWrite(WRIST_L_SPEED_PIN, 0);
    digitalWrite(WRIST_R1_PIN, LOW);
    digitalWrite(WRIST_R2_PIN, LOW);
    analogWrite(WRIST_R_SPEED_PIN, 0);
    digitalWrite(CLAW_OPEN, LOW);
    digitalWrite(CLAW_CLOSE, LOW);
    stopped = true;

#if DEBUG_MODE == 1
    Serial.println("Stopped motors");
#endif
  }
}

void updateServos()
{
  base.write(base_speed);
  shoulder.write(shoulder_pos);
  elbow.write(elbow_pos);
#if DEBUG_MODE
//  Serial.print("shoulder: ");
//  Serial.println(shoulder_pos);
//  Serial.print("elbow: ");
//  Serial.println(elbow_pos);
#endif
  if (claw_dir == 2) {
    digitalWrite(CLAW_OPEN, HIGH);
    digitalWrite(CLAW_CLOSE, LOW);
  } else if (claw_dir == 0) {
    digitalWrite(CLAW_OPEN, LOW);
    digitalWrite(CLAW_CLOSE, HIGH);
  } else {
    digitalWrite(CLAW_OPEN, LOW);
    digitalWrite(CLAW_CLOSE, LOW);
  }
  wristPhi_speed = int(wristPhi_speed);
  wristTheta_speed = int(wristTheta_speed);

  int offset = 0;
  // Right now we can't rotate and tilt ar the same time we'll need to fix this later
  if (wristTheta_speed > 0)
  {
    digitalWrite(WRIST_L1_PIN, HIGH);
    digitalWrite(WRIST_L2_PIN, LOW);
    analogWrite(WRIST_L_SPEED_PIN, abs(wristTheta_speed + offset) * 2);
    digitalWrite(WRIST_R1_PIN, HIGH);
    digitalWrite(WRIST_R2_PIN, LOW);
    analogWrite(WRIST_R_SPEED_PIN, abs(wristTheta_speed + offset) * 2);
    Serial.print("wrist go up: ");
    Serial.println(abs(wristTheta_speed + offset) *2);
    
    return;
  }
  if (wristTheta_speed < 0)
  {
    digitalWrite(WRIST_L1_PIN, LOW);
    digitalWrite(WRIST_L2_PIN, HIGH);
    analogWrite(WRIST_L_SPEED_PIN, abs(wristTheta_speed + offset) * 2);
    digitalWrite(WRIST_R1_PIN, LOW);
    digitalWrite(WRIST_R2_PIN, HIGH);
    analogWrite(WRIST_R_SPEED_PIN, abs(wristTheta_speed + offset) * 2);
    Serial.println("wrist go down");
    return;
  }
  if (wristPhi_speed > 0)
  {
    digitalWrite(WRIST_L1_PIN, HIGH);
    digitalWrite(WRIST_L2_PIN, LOW);
    analogWrite(WRIST_L_SPEED_PIN, abs(wristPhi_speed + offset) * 2);
    digitalWrite(WRIST_R1_PIN, LOW);
    digitalWrite(WRIST_R2_PIN, HIGH);
    analogWrite(WRIST_R_SPEED_PIN, abs(wristPhi_speed + offset) * 2);
    Serial.println("wrist rolls right"); 

    return;
  }
  if (wristPhi_speed < 0)
  {
    digitalWrite(WRIST_L1_PIN, LOW);
    digitalWrite(WRIST_L2_PIN, HIGH);
    analogWrite(WRIST_L_SPEED_PIN, abs(wristPhi_speed + offset) * 2);
    digitalWrite(WRIST_R1_PIN, HIGH);
    digitalWrite(WRIST_R2_PIN, LOW);
    analogWrite(WRIST_R_SPEED_PIN, abs(wristPhi_speed + offset) * 2);
    Serial.println("wrist roll left");
    return;
  }
  if (wristPhi_speed == 0 && wristTheta_speed == 0)
  {
    digitalWrite(WRIST_L1_PIN, LOW);
    digitalWrite(WRIST_L2_PIN, LOW);
    analogWrite(WRIST_L_SPEED_PIN, 0);
    digitalWrite(WRIST_R1_PIN, LOW);
    digitalWrite(WRIST_R2_PIN, LOW);
    analogWrite(WRIST_R_SPEED_PIN, 0);
  }
}
