#include <EtherCard.h>
#include <IPAddress.h>
#include <Servo.h>

/*
 * TODO: 
 *  - configure base station side to send the correct numbers.
 *  - fix linActuator limit switches to only move up when down limit is on and only down when up is on.
 */


/*
 * NANO PWM pins: D3, D5, D6, D9, D10, D11
 * 
 * PINS USED BY ETHERNET SHEILD: D10, D11, D12, D13 (it uses SPI)
 * 
 * USING TALONS TO CONTROL ALL MOTORS (ACTYUATOR/CAROUSEL) -> TREAT EACH MOTOR AS A CONTINUOUS SERVO
 *  The carousel and linear actuator are going to have external limit switches to monitor their positions.
 * 
 * LINEAR ACTUATOR - D2/D3
 * CAROUSEL - D5
 *  - limit switch - A4

 * FAN - D6
 * MICROSCOPE - D7/D8
 *    - encoder - A5
 */

// Set equal to 1 for serial debugging
#define DEBUG 1

// 2 is the drill ID
#define DEVICE_ID 2

// Note: analogWrite() can not be used on pins 9 or 10 because of the servo library.
// Servos can still be used on those pins though
#define ACTUATOR_UP_PIN 2 // which pin is up depends on wiring. Can be reversed
#define ACTUATOR_DOWN_PIN 3

#define CAROUSEL_PIN 5
#define CAROUSEL_LIMIT_PIN A4

#define FAN_PIN 6
#define MICROSCOPE_UP_PIN 7
#define MICROSCOPE_DOWN_PIN 8
#define MICROSCOPE_ENCODER_PIN A5

// servo objects for talon motor controllers
Servo carousel, fan;

// ethernet interface ip address (static ip)
static byte myip[] = {10, 0, 0, 103};
//static byte myip[] = {192, 168, 1, 101};
static int myport = 1003;
// gateway ip address
static byte gwip[] = {10, 0, 0, 1};
//static byte gwip[] = {192, 168, 1, 1};
// ethernet mac address - must be unique on your network
static byte mymac[] = {0xAC, 0xDC, 0x0D, 0xAD, 0x00, 0x00};
// tcp/ip send and receive buffer
byte Ethernet::buffer[500];

// raw bytes to store from ethernet data
// they are converted to output ranges in updateServos()
uint8_t myHash = 0;
uint8_t serialHash = 0;
int linearActuatorSpeed = 127;
int carouselSpeed = 1;
int fanSpeed = 90;
int microscopePosition = 1;

bool carouselMoving = false;
bool linearActuatorMoving = false;

unsigned long stopTimeout = 0, turnTimeout = 0;

// callback that prints received packets to the serial port
void udpSerialPrint(uint16_t dest_port, uint8_t src_ip[IP_LEN], uint16_t src_port, const char *data, uint16_t len)
{
  IPAddress src(src_ip[0], src_ip[1], src_ip[2], src_ip[3]);

  // SCIENCE msg: [startByte, deviceID, linearActuator, carousel, fan, microscope, checkSum]
  // hash = (sum of data bytes) / (num of bytes) - Don't include startByte or deviceID in sum

  #if DEBUG
    for (int i = 0; i < len; i++) {
      Serial.print(uint8_t(data[i]));
      Serial.print(", ");
    }
    Serial.print("\n");
  #endif

  if (len >= 2) {
    if (uint8_t(data[0]) != 255) { // check for 255, the startByte for science
      #if DEBUG
        Serial.println("Message does not start with 255!");
      #endif
      return;
    }

    if (data[1] == DEVICE_ID) { // check for correct deviceID. useful if science is using multiple arduinos
      if (len != 7) {
        #if DEBUG
          Serial.println("Drill message is wrong length!");
        #endif
        return;
      }
      linearActuatorSpeed = uint8_t(data[2]);
      carouselSpeed = uint8_t(data[3]);
      fanSpeed = uint8_t(data[4]);
      microscopePosition = uint8_t(data[5]);

      serialHash = uint8_t(data[6]);
      myHash = (linearActuatorSpeed + carouselSpeed + fanSpeed + microscopePosition) & 0xff;
      if (myHash == serialHash) {
        updateServos();
        stopTimeout = millis();
      }
      #if DEBUG
      else {
        Serial.println("Bad hash!");
      }
      #endif
    }
    else { // unknown ID
      #if DEBUG
        Serial.println("Unknown device id!");
      #endif
      return;
    }
  }
}

void setup()
{
    // setup motors
  pinMode(ACTUATOR_UP_PIN, OUTPUT);
  pinMode(ACTUATOR_DOWN_PIN, OUTPUT);
  pinMode(MICROSCOPE_UP_PIN, OUTPUT);
  pinMode(MICROSCOPE_DOWN_PIN, OUTPUT);
  digitalWrite(ACTUATOR_UP_PIN, LOW);
  digitalWrite(ACTUATOR_DOWN_PIN, LOW);
  digitalWrite(MICROSCOPE_UP_PIN, LOW);
  digitalWrite(MICROSCOPE_DOWN_PIN, LOW);

  carousel.attach(CAROUSEL_PIN, 900, 2100);
  fan.attach(FAN_PIN, 900, 2100);
  // all motors should start in neutral position (resting for motors, 90 degrees for servos)
  carousel.write(90);
  fan.write(90);

  pinMode(CAROUSEL_LIMIT_PIN, INPUT_PULLUP); // digital signal
  pinMode(MICROSCOPE_ENCODER_PIN, INPUT); // analog signal

  Serial.begin(9600);
  #if DEBUG
    Serial.begin(9600);
    if (ether.begin(sizeof Ethernet::buffer, mymac, 10) == 0)
      Serial.println(F("Failed to access Ethernet controller"));
  #else
    ether.begin(sizeof Ethernet::buffer, mymac, 10);
  #endif

  ether.staticSetup(myip, gwip);
  #if DEBUG
    ether.printIp("IP:  ", ether.myip);
    ether.printIp("GW:  ", ether.gwip);
    ether.printIp("DNS: ", ether.dnsip);
  #endif

  // register udpSerialPrint() to port
  ether.udpServerListenOnPort(&udpSerialPrint, myport);

}

void loop()
{
  // this must be called for ethercard functions to work.
  ether.packetLoop(ether.packetReceive());

  // If switch is triggered while carousel is moving, stop carousel. This should allign test tube properly
 if(!digitalRead(CAROUSEL_LIMIT_PIN) && carouselMoving && (carouselSpeed == 1)) {
   Serial.println("limited");
   carousel.write(90);
   carouselMoving = false;
 }
 //Serial.println(analogRead(MICROSCOPE_ENCODER_PIN));

  unsigned long curr_time = millis();
  // stop all motors after 1 second of no messages
  if (curr_time - stopTimeout >= 3000) {
    stopTimeout = millis();
    carousel.write(90);
    fan.write(90);

    #if DEBUG
      Serial.println("Stopped motors");
    #endif
  }

  delay(5);
}

void updateServos() {
  // update linear actuator
  if(linearActuatorSpeed > 127) {
    digitalWrite(ACTUATOR_UP_PIN, HIGH);
  }
  else if (linearActuatorSpeed < 127) {
    digitalWrite(ACTUATOR_DOWN_PIN, HIGH);
  }
  else {
    digitalWrite(ACTUATOR_UP_PIN, LOW);
    digitalWrite(ACTUATOR_DOWN_PIN, LOW);
  }

  //update carousel
  if(carouselSpeed==0) { //if carousel already moving, no need to call write function again
    carousel.write(130);
    carouselMoving = true;
  }
  else if(carouselSpeed==2) {
    carousel.write(50);
    carouselMoving = true;
  }
  else if (carouselSpeed == 1) {}
  
  //update claw
  fan.write(fanSpeed);

  //update microscope
  if(microscopePosition == 0) {
    digitalWrite(MICROSCOPE_UP_PIN, HIGH);
  }
  else if(microscopePosition == 2) {
    digitalWrite(MICROSCOPE_DOWN_PIN, HIGH);
  }
  else {
    digitalWrite(MICROSCOPE_UP_PIN, LOW);
    digitalWrite(MICROSCOPE_DOWN_PIN, LOW);
  }
}
