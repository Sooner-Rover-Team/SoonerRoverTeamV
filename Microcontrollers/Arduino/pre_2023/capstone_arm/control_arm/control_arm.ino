#include <Ethernet.h>
#include <EthernetUdp.h>

// Port K bits (pins) for encoders
#define ENC_BASE_A 0x01     // pin A8
#define ENC_BASE_B 0x02     // pin A9
#define ENC_SHOULDER_A 0x04 // pin A10
#define ENC_SHOULDER_B 0x08 // pin A11
#define ENC_ELBOW_A 0x10    // pin A12
#define ENC_ELBOW_B 0x20    // pin A13
#define ENC_WRISTP_A 0x40   // pin A14
#define ENC_WRISTP_B 0x80   // pin A15

// Encoder position limits
#define MIN_BASE -500          // update this!
#define MAX_BASE 500           // update this!
#define MIN_SHOULDER 0
#define MAX_SHOULDER 1100
#define MIN_ELBOW 0
#define MAX_ELBOW 310
#define MIN_WRISTP -278
#define MAX_WRISTP 295

// pins for inputs
#define PIN_B_OPEN 14
#define PIN_B_CLOSE 15
#define PIN_J_ROLL A7

// program control values
#define MESSAGE_PERIOD 100
#define MESSAGE_LENGTH 14
#define DEVICE_ID 1
#define DEBUG_PERIOD 500

// encoder positions - updated by interrupt
volatile int eBase = 0;
volatile int eShoulder = 0;
volatile int eElbow = 0;
volatile int eWristP = 0;
volatile byte port_k_prev = 0x00; // only used by ISR

// test program vars
unsigned long timeMessage, timePrint;
bool bClawO, bClawC;
int jWristR;

char message[14]; // the bytes we send out over UDP
EthernetUDP Udp;
// ethernet mac address - must be unique on your network
static byte mymac[] = { 0x69, 0x69, 0x69, 0x69, 0x69, 0x69 };
// control arm address (this)
IPAddress myip(192, 168, 1, 69);
const int srcPort PROGMEM = 4321;
// rover arm address
IPAddress dstip(192, 168, 1, 140);
const int dstPort PROGMEM = 2040;

void setup() {
  // setup encoder pins and interrupts
  cli();
  DDRK &= 0x00; // set encoder pins (all 8 port k bits) as inputs
  PORTK |= 0xFF; // enable pullups on encoder pins
  PCICR |= 0x04; // enable port K pin change interrupt
  PCMSK2 |= 0xFF; // enable interrupt for all port K pins
  sei();

  port_k_prev = PINK;

  // setup inputs
  pinMode(PIN_B_OPEN, INPUT);
  digitalWrite(PIN_B_OPEN, HIGH);
  pinMode(PIN_B_CLOSE, INPUT);
  digitalWrite(PIN_B_CLOSE, HIGH);
  pinMode(PIN_J_ROLL, INPUT);
  
  // setup serial
  Serial.begin(9600);

  // setup ethernet
  Ethernet.init(10);
  Ethernet.begin(mymac, myip);
  if (Ethernet.hardwareStatus() == EthernetNoHardware) {
    Serial.println("Ethernet shield was not found.  Sorry, can't run without hardware. :(");
    while (true) {
      delay(1); // do nothing, no point running without Ethernet hardware
    }
  }
  if (Ethernet.linkStatus() == LinkOFF) {
    Serial.println("Ethernet cable is not connected.");
  }
  Udp.begin(srcPort);

  // initalize message buffer
  message[0] = -127; // "start message" byte
  message[1] = DEVICE_ID;
}

void loop() {
  // update non-encoder inputs
  bClawO = !digitalRead(PIN_B_OPEN); // active low - pul up
  bClawC = !digitalRead(PIN_B_CLOSE);
  jWristR = analogRead(PIN_J_ROLL);

  // update message buffer
  
  // (-127), Device ID (1), base (high), base (low),
  // shoulder (high), shoulder (low), elbow (high), elbow (low),
  // wrist pitch (high), wrist pitch (low),
  // wrist roll (joystick high), wrist roll (joystick low),
  // buttons, hash
  
  // 2 byte encoder positions (most siginificant byte first)
  message[2] = (char)(eBase >> 8);
  message[3] = (char)(eBase);
  message[4] = (char)(eShoulder >> 8);
  message[5] = (char)(eShoulder);
  message[6] = (char)(eElbow >> 8);
  message[7] = (char)(eElbow);
  message[8] = (char)(eWristP >> 8);
  message[9] = (char)(eWristP);
  // 2 byte joystick position
  message[10] = (char)(jWristR >> 8);
  message[11] = (char)(jWristR);
  // buttons - each bit is one button
  message[12] = 0x00;
  if (bClawO)
    message[12] |= 0x01;
  if (bClawC)
    message[12] |= 0x02;
  // hash - (average of bytes [2...12])
  message[13] = (message[2] + message[3] + message[4] + message[5] + message[6] + message[7] + message[8] + message[9] + message[10] + message[11] + message[12]) / 11;
  
  
  // DEBUG: periodically display encoder positions
  if (millis()-timePrint > DEBUG_PERIOD)
  {
    timePrint = millis();

    Serial.print("B: " + String(eBase));
    Serial.print("\tS: " + String(eShoulder));
    Serial.print("\tE: " + String(eElbow));
    Serial.print("\tW: " + String(eWristP));
    Serial.print("\tbO: " + String(bClawO));
    Serial.print("\tbC: " + String(bClawC));
    Serial.println("\tjR: " + String(jWristR));
  }

  // periodically send messages
  if (millis()-timeMessage > MESSAGE_PERIOD)
  {
    timeMessage = millis();

    Udp.beginPacket(dstip, dstPort);
    /*
    // DEBUG: print message contents
    for(int i = 0; i < MESSAGE_LENGTH; i++)
    {
      Udp.write(message[i]);
      Serial.print(int(message[i]));
      Serial.print(", ");
    }
    Serial.print("\n");
    */
    Udp.write(message, MESSAGE_LENGTH);
    Udp.endPacket();
  }
}

ISR(PCINT2_vect) // pin change interrupt for pins A8 to A15 (update encoder positions)
{
  byte port_k_pins = PINK;

  // base
  if ((port_k_pins & ENC_BASE_A) && !(port_k_prev & ENC_BASE_A)) // rising edge on A
  {
    if (port_k_pins & ENC_BASE_B)
      eBase--; // CCW
    else
      eBase++; // CW
  }
  else if (!(port_k_pins & ENC_BASE_A) && (port_k_prev & ENC_BASE_A)) // falling edge on A
  {
    if (port_k_pins & ENC_BASE_B)
      eBase++; // CW
    else
      eBase--; // CCW
  }

  // shoulder
  if ((port_k_pins & ENC_SHOULDER_A) && !(port_k_prev & ENC_SHOULDER_A)) // rising edge on A
  {
    if (port_k_pins & ENC_SHOULDER_B)
      eShoulder--; // CCW
    else
      eShoulder++; // CW
  }
  else if (!(port_k_pins & ENC_SHOULDER_A) && (port_k_prev & ENC_SHOULDER_A)) // falling edge on A
  {
    if (port_k_pins & ENC_SHOULDER_B)
      eShoulder++; // CW
    else
      eShoulder--; // CCW
  }

  // elbow
  if ((port_k_pins & ENC_ELBOW_A) && !(port_k_prev & ENC_ELBOW_A)) // rising edge on A
  {
    if (port_k_pins & ENC_ELBOW_B)
      eElbow--; // CCW
    else
      eElbow++; // CW
  }
  else if (!(port_k_pins & ENC_ELBOW_A) && (port_k_prev & ENC_ELBOW_A)) // falling edge on A
  {
    if (port_k_pins & ENC_ELBOW_B)
      eElbow++; // CW
    else
      eElbow--; // CCW
  }

  // wrist pitch
  if ((port_k_pins & ENC_WRISTP_A) && !(port_k_prev & ENC_WRISTP_A)) // rising edge on A
  {
    if (port_k_pins & ENC_WRISTP_B)
      eWristP--; // CCW
    else
      eWristP++; // CW
  }
  else if (!(port_k_pins & ENC_WRISTP_A) && (port_k_prev & ENC_WRISTP_A)) // falling edge on A
  {
    if (port_k_pins & ENC_WRISTP_B)
      eWristP++; // CW
    else
      eWristP--; // CCW
  }
  
  port_k_prev = port_k_pins;
}
