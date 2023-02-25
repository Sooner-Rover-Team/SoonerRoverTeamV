#include <EtherCard.h>
#include <IPAddress.h>
#include <Servo.h>

// Set to 1 for serial debugging
#define DEBUG_MODE 1

// 1 is the arm ID
#define DEVICE_ID 1
 
/*
 * *********************
 * Ethernet/ UDP Setup *
 * *********************
 */

// ethernet interface ip address (static ip)
static byte myip[] = {10, 0, 0, 102}; // use this ip when installed on rover router
//static byte myip[] = {192, 168, 0, 200}; // 192.168.0.x comes from router ip, and x is random to give unique ID.
static int myport = 1002; //5005;

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
// used to check for errors in received data
uint8_t myHash = 0;
uint8_t serialHash = 0;

// stores data received from UDP. Data is for motor movement/ positions
int base = 0;
int bicepPosition = 0;
int forearmPosition = 0;
int wristAngle = 0;
int wristRotation = 0;
int clawDir = 0;


// these variables are to measure how long it's been since last msg was recieved
unsigned long Timeout = 0;

// Once UDP data is received, send those variables through CAN using this function
void sendToCAN() {

}


// callback that prints received packets to the serial port
void udpSerialPrint(uint16_t dest_port, uint8_t src_ip[IP_LEN], uint16_t src_port, const char *data, uint16_t len)
{
  IPAddress src(src_ip[0], src_ip[1], src_ip[2], src_ip[3]);

  // if data[0] or data[1] are incorrect, or errors occur in the values, the function prints a error msg and returns.
  // In practice, incorrect msgs are ignored and we would have no idea an error occured

  // arm msg: [255, 1, base, bicep, elbow, wristAngle, wristRotation, clawDir, checksum]
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
    if (uint8_t(data[0]) != 255) { // start message should always be 255
      #if DEBUG_MODE == 1
        Serial.println("Message does not start with 255!");
      #endif
      return;
    }

    if (data[1] == DEVICE_ID){ // makes sure data is for arm
      
      if (len != 9) {
        #if DEBUG_MODE == 1
          Serial.println("Drill message is wrong length!");
        #endif
        return;
      }
      
      // data[] will get overwritten with each msg, so we must save as variables here to use later
        base = uint8_t(data[2]);
        bicepPosition = uint8_t(data[3]);
        forearmPosition = uint8_t(data[4]);
        wristAngle = uint8_t(data[5]);
        wristRotation = uint8_t(data[6]);
        clawDir = uint8_t(data[7]);
        

      serialHash = uint8_t(data[8]); 
      // the hash checks for errors. If a bit was incorrectly translated, the sum will be different from the serialHash
      // there is an unlikely edge case where an error in the values and an error in the serialHash occurs, making them
      // equal when they should not be.
      myHash = (base + bicepPosition + forearmPosition + wristAngle + wristRotation + clawDir) & 0xff;
      if (myHash == serialHash)
      {
        sendToCAN();
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
    }
  }
}

void setup()
{
  
#if DEBUG_MODE == 1
  Serial.begin(9600);
  if (ether.begin(sizeof Ethernet::buffer, mymac, 10) == 0) //configures the ethernet sheild
    Serial.println(F("Failed to access Ethernet controller"));
#else
  ether.begin(sizeof Ethernet::buffer, mymac, 10);
#endif

  
  // set up static configuration (other option is automatic setup which creates a unique ip. If we used auto we would
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

  if ( millis() - timeOut >= 1000) // if the last good msg recieved was longer than 1 sec ago, stop all motors
  {
    timeOut = millis();
    // stopped position of motors
    base = 90;
    bicepPosition = 180;
    forearmPosition = 180;
    wristAngle = 0;
    wristRotation = 0;
    clawDir = 0;
    
    #if DEBUG
    Serial.println("Stopped motors");
    #endif
  }
}
