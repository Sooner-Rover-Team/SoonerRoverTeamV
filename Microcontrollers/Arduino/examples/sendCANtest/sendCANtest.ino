// demo: CAN-BUS Shield, send data
// loovee@seeed.cc


#include <SPI.h>

#define CAN_2515
// #define CAN_2518FD

// Set SPI CS Pin according to your hardware

#if defined(SEEED_WIO_TERMINAL) && defined(CAN_2518FD)
// For Wio Terminal w/ MCP2518FD RPi Hat：
// Channel 0 SPI_CS Pin: BCM 8
// Channel 1 SPI_CS Pin: BCM 7
// Interupt Pin: BCM25
const int SPI_CS_PIN  = BCM8;
const int CAN_INT_PIN = BCM25;
#else

// For Arduino MCP2515 Hat:
// the cs pin of the version after v1.1 is default to D9
// v0.9b and v1.0 is default D10
const int SPI_CS_PIN = 10;
const int CAN_INT_PIN = 2;
#endif


#ifdef CAN_2518FD
#include "mcp2518fd_can.h"
mcp2518fd CAN(SPI_CS_PIN); // Set CS pin
#endif

#ifdef CAN_2515
#include "mcp2515_can.h"
mcp2515_can CAN(SPI_CS_PIN); // Set CS pin
#endif

void setup() {
    SERIAL_PORT_MONITOR.begin(9600);
    while(!Serial){};

    while (CAN_OK != CAN.begin(CAN_100KBPS)) {             // init can bus : baudrate = 500k
        SERIAL_PORT_MONITOR.println("CAN init fail, retry...");
        delay(100);
    }
    SERIAL_PORT_MONITOR.println("CAN init ok!");
}

unsigned char stmp[5];
void loop() {
    // send data:  id = 0x00, standrad frame, data len = 8, stmp: data buf
    // stmp[7] = stmp[7] + 1;
    // if (stmp[7] == 100) {
    //     stmp[7] = 0;
    //     stmp[6] = stmp[6] + 1;

    //     if (stmp[6] == 100) {
    //         stmp[6] = 0;
    //         stmp[5] = stmp[5] + 1;
    //     }
    // }
    // Serial.println("base: ");
    // // get the value the user inputs
    // while (Serial.available() == 0) {}// this waits for someone to press enter with text in the Serial input.
    // String userInput1 = Serial.readString(); // read the text (given by the user) as a String object.
    // int c1 = userInput1.toInt(); // convert the String into an int (integer) variable.

    // Serial.println("bicep: ");
    // // get the value the user inputs
    // while (Serial.available() == 0) {}// this waits for someone to press enter with text in the Serial input.
    // userInput1 = Serial.readString(); // read the text (given by the user) as a String object.
    // int c2 = userInput1.toInt(); // convert the String into an int (integer) variable.
    
    // Serial.println("forearm: " );
    // // get the value the user inputs
    // while (Serial.available() == 0) {}// this waits for someone to press enter with text in the Serial input.
    // userInput1 = Serial.readString(); // read the text (given by the user) as a String object.
    // int c3 = userInput1.toInt(); // convert the String into an int (integer) variable.
    int c1 = 126, c2 = 126, c3 = 95;
    unsigned char stmp[] = {0x01, c1, c2, c3, c1+c2+c3};

    CAN.MCP_CAN::sendMsgBuf(0x01, 0, 5, stmp); // id = 0x00, standrad frame, data len = 8, stmp: data buf
    SERIAL_PORT_MONITOR.print("CAN sent: ");
    for(int i=0; i<5; ++i) {
      SERIAL_PORT_MONITOR.print(stmp[i]);
      SERIAL_PORT_MONITOR.print(", ");
    }
    SERIAL_PORT_MONITOR.println();
    delay(100);
}

// END FILE
