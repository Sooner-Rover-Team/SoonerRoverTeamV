#include <EtherCard.h>
#include <IPAddress.h>
#include <Servo.h>

/*
 * #define creates special variabels can van only be used with #if/#endif
 * #if/#endif control whether lines of code get compiled or not. 
 * 
 * This UDP client is set up with a static IP so we can send msgs to the right controller every time (i think)
 * In this config, the arduino is the host with a non-changing IP so we can reliably send msgs.
 * The myip is based off the router, where the last number is a unique ID for the host.
 * gwip is the private ip of the router.
 * port can be any unused port on the router network
 */
 
 // Set equal to 1 for serial debugging
#define DEBUG_MODE 1

// 2 is the drill ID
#define DEVICE_ID 2
 
/*
 * *********************
 * Ethernet/ UDP Setup *
 * *********************
 */

// ethernet interface ip address (static ip)
static byte myip[] = {10, 0, 0, 103}; // use this ip when installed on rover router
//static byte myip[] = {192, 168, 0, 200}; // 192.168.0.x comes from router ip, and x is random to give unique ID.
static int myport = 1003; //5005;

// gateway ip address
static byte gwip[] = {10, 0, 0, 1}; // use this gwip when installed on rover router
//static byte gwip[] = {192, 168, 0, 1}; 

// ethernet mac address - must be unique on your network
static byte mymac[] = {0xAC, 0xDC, 0x0D, 0xAD, 0x00, 0x00}; 

// tcp/ip send and receive buffer
byte Ethernet::buffer[500];

/* *****************************
 * Variables for recieved data *
 * *****************************
 */

// raw bytes to store from ethernet data
// they are converted to output ranges in updateServos()
uint8_t myHash = 0;
uint8_t serialHash = 0;

char actuatorDir = 2; // 0 is down, 1 is up, 2 is neither (not moving)
int actuatorSpeed = 0;
int drillSpeed = 0;
int fanSpeed = 0;
int carouselSpeed = 0;
char carouselTurn = 0;

int turnTime = 350;
char turning = 0;

// these variables are to measure how long it's been since last msg was recieved
unsigned long stopTimeout = 0, turnTimeout = 0;

Servo linActuator, claw, base; // 3 motor movements on science package. Using Talons to control all 3, so PWM is needed.

void updateServos() {
  actuatorSpeed = map(actuatorSpeed, 0, 10, 1000, 2000); // -10 maps to 1000, 0 maps to 1500, +10 maps to 2000
  Serial.print("Servo is receiving this value: ");
  Serial.print(actuatorSpeed);
  
  linActuator.writeMicroseconds(actuatorSpeed);
}


// callback that prints received packets to the serial port
void udpSerialPrint(uint16_t dest_port, uint8_t src_ip[IP_LEN], uint16_t src_port, const char *data, uint16_t len)
{
  IPAddress src(src_ip[0], src_ip[1], src_ip[2], src_ip[3]);

  // if data[0] or data[1] are incorrect, or errors occur in the values, the function prints a error msg and returns.
  // In practice, incorrect msgs are ignored and we would have no idea an error occured

  #if DEBUG_MODE == 1
    for (int i = 0; i < len; i++) // print all msgs we recieved
    {
      Serial.print(uint8_t(data[i]));
      Serial.print(", ");
    }
    Serial.print("\n");
  #endif

  // check for 255, message type
  if (len >= 2){
    if (uint8_t(data[0]) != 255) { // start message should always be 255 for science package
      #if DEBUG_MODE == 1
        Serial.println("Message does not start with 255!");
      #endif
      return;
    }

    if (data[1] == DEVICE_ID){ // if message is actually for the science module
      /*
      if (len != 9) {
        #if DEBUG_MODE == 1
          Serial.println("Drill message is wrong length!");
        #endif
        return;
      }
      */
      // data[] will get overwritten with each msgs, so we must save as variables here to use later
      actuatorSpeed = uint8_t(data[2]);

      serialHash = uint8_t(data[3]); 
      // the hash checks for errors. If a bit was incorrectly translated, the sum will be different from the serialHash
      // there is an unlikely edge case where an error in the values and an error in the serialHash occurs, making them
      // equal when they should not be.
      myHash = actuatorSpeed; //(actuatorDir + actuatorSpeed + drillSpeed + fanSpeed + carouselSpeed + carouselTurn) & 0xff;
      if (myHash == serialHash)
      {
        Serial.println("Hash was right, updating servo");
        updateServos();
      }
      #if DEBUG_MODE == 1
      else
      {
        Serial.println("Bad hash!");
      }
      #endif
    }
    else // if device_ID is wrong:
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
  linActuator.attach(6); //D6
  
#if DEBUG_MODE == 1
  Serial.begin(9600);
  if (ether.begin(sizeof Ethernet::buffer, mymac, 10) == 0) //configures the ethernet sheild
    Serial.println(F("Failed to access Ethernet controller"));
#else
  ether.begin(sizeof Ethernet::buffer, mymac, 10);
#endif

  // set up static configuration (other option is automatic setup which creates a unique ip. If we used this we would
  //  would have no idea what the arduino is and the base station wouldn't know where to send msgs
  ether.staticSetup(myip, gwip); 

  ether.printIp("IP:  ", ether.myip);
  ether.printIp("GW:  ", ether.gwip);
  ether.printIp("DNS: ", ether.dnsip);

  // register udpSerialPrint() to port. when a msg is recieved, udpSerialPrint is automatically called
  ether.udpServerListenOnPort(&udpSerialPrint, myport);
}

void loop()
{
  // this must be called for ethercard functions to work.
  ether.packetLoop(ether.packetReceive());
}
