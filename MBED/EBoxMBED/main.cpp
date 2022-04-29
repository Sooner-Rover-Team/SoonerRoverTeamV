#include "mbed.h"
// Import official mbed-os library from:
// https://github.com/ARMmbed/mbed-os
#include "EthernetInterface.h"
// Import from https://os.mbed.com/users/tecnosys/code/mcp2515/
#include "CAN3.h"

// byte to signify start of communication
// can be any byte it does not matter
#define startbyte 0x23
// port to listen on
#define PORT 80
// debug and debug printing, disable when
// actually using
#define DEBUG 0
#define dbprint(fmt, ...) do {if (DEBUG) printf(fmt, __VA_ARGS__); } while (0);

// Network interface
EthernetInterface net;

// SPI definition
SPI spi(p11,p12,p13);

// LEDS
DigitalOut led1(LED1);
DigitalOut led2(LED2);
DigitalOut led3(LED3);

// Timeout for blinking and reseting wheels (not implemented yet)
Timeout blink, wheelreset;

// Chip Select
DigitalOut cs1(p14);
DigitalOut relay(p16);

// CAN interface
CAN3 can(spi, p14, p15);

// callback
void LEDOff() {
    led2 = 0;
}

// send the wheel speeds over CAN
void sendWheelSpeeds(char *speeds, char cs) {
    speeds[7] = cs;
    CANMessage c_msg(1, speeds, 8, CANData, CANStandard);
    can.write(&c_msg);
    dbprint("data has been written\n",0);
}

// check if the message is stop
int isStop(char *speeds) {
    for (int i = 0; i < 6; i++) {
        if (speeds[i] != 126)
            return 0;
    }
    return 1;
}

// turn the wheels on and off, not implemented yet
void toggleWheels() {
    relay = !relay;
    led3 = !led3;
}


int main()
{
    led1 = 0;
    relay = 0;
    led2 = 0;
    led3 = 1;
    can.frequency(8000000);
    // Bring up the ethernet interface
    dbprint("Setting up UDP Socket over ethernet\n",0);
    net.connect();

    // Show the network address
    SocketAddress a;
    net.get_ip_address(&a);
    while(!a.get_ip_address()) {
        net.get_ip_address(&a);
    }
    dbprint("IP address: %s\n", a.get_ip_address() ? a.get_ip_address() : "None");
    if (a.get_ip_address())
        led1 = 1;
    

    // Open a socket on the network interface
    UDPSocket socket;
    socket.open(&net);
    // Listen on port 80
    socket.bind(PORT);
    
    // create variables for holding datas
    char data[9];
    char speeds[6];
    char stopmsg = 0;
    while (1) {
        // receive the data
        int size = socket.recv(data,PORT);
        if (DEBUG) {
            printf("data: %s\n",data);
            for (int i = 0; i < size; i++) {
                printf("%x ",data[i]);
            }
            printf("\n");
        }
        // if the message start is correct
        if (data[0] == startbyte) {
            dbprint("Start of message\n",0);
            if (data[1] == 0x00) {
                dbprint("Message to move wheel\n",0);
                int cs = 0;
                for (int i = 2; i < 8; i++) {
                    dbprint("wheel %d speed: %d\n",i-1,data[i]);
                    cs += data[i];
                    speeds[i-2] = data[i];
                }
                // checksum
                cs &= 0xff;
                if (data[8] == cs) {
                    dbprint("checksum verified: %x\n",cs);
                    if (isStop(speeds)) {
                        if (!stopmsg) {
                            sendWheelSpeeds(speeds,cs);
                            stopmsg = 1;
                            led2 = 1;
                            dbprint("wheel speeds sent\n",0);
                        }
                    } else {
                        sendWheelSpeeds(speeds,cs);
                        stopmsg = 0;
                        led2 = 1;
                        dbprint("wheel speeds sent\n",0);
                    }
                    blink.attach(&LEDOff, .2f);

                }
                else
                    dbprint("checksum failed, cs: %d, data[8]: %d\n",cs,data[8]);
            }
            else if (data[1] = 0x01) {
                dbprint("message to toggle the wheels\n",0);
                toggleWheels();
            }
        }
        // set data to 0
        memset(data, 0, sizeof(data));
    }

    // Close the socket to return its memory and bring down the network interface
    socket.close();

    // Bring down the ethernet interface
    net.disconnect();
    dbprint("Done\n",0);
}
