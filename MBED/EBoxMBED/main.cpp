#include "mbed.h"
// Import official mbed-os library from:
// https://github.com/ARMmbed/mbed-os
#include "EthernetInterface.h"
// Import from https://os.mbed.com/users/tecnosys/code/mcp2515/
#include "CAN3.h"

#define startbyte 0x23
#define PORT 80
#define DEBUG 1

// Network interface
EthernetInterface net;

// SPI definition
SPI spi(p11,p12,p13);

// Chip Select
DigitalOut cs1(p14);

// CAN interface
CAN3 can(spi, p14, p15);

void sendWheelSpeeds(char *speeds) {
    printf("speed 1: %d\n",speeds[0]);
    CANMessage c_msg(1, speeds, 8, CANData, CANStandard);
    can.write(&c_msg);
}

// Socket demo
int main()
{
    can.frequency(8000000);
    // Bring up the ethernet interface
    if (DEBUG) printf("Setting up UDP Socket over ethernet\n");
    net.connect();

    // Show the network address
    SocketAddress a;
    net.get_ip_address(&a);
    if (DEBUG) printf("IP address: %s\n", a.get_ip_address() ? a.get_ip_address() : "None");

    // Open a socket on the network interface
    UDPSocket socket;
    socket.open(&net);
    // Listen on port 80
    socket.bind(PORT);
    char data[9];
    char speeds[6];
    while (1) {
        int size = socket.recv(data,PORT);
        if (DEBUG) {
            printf("data: %s\n",data);
            for (int i = 0; i < size; i++) {
                printf("%x ",data[i]);
            }
            printf("\n");
        }
        if (data[0] == startbyte) {
            if (DEBUG) printf("Start of message\n");
            if (data[1] == 0x00) {
                if (DEBUG) printf("Message to move wheel\n");
                int cs = 0;
                for (int i = 2; i < 8; i++) {
                    if (DEBUG) printf("wheel %d speed: %d\n",i-1,data[i]);
                    cs += data[i];
                    speeds[i-2] = data[i];
                }
                cs &= 0xff;
                if (data[8] == cs) {
                    if (DEBUG) printf("checksum: %d, verified\n",cs);
                    sendWheelSpeeds(speeds);
                    printf("wheel speeds sent\n");
                }
                else
                    if (DEBUG) printf("checksum failed, cs: %d, data[8]: %d\n",cs,data[8]);
            }
        }
        memset(data, 0, sizeof(data));
    }

    // Close the socket to return its memory and bring down the network interface
    socket.close();

    // Bring down the ethernet interface
    net.disconnect();
    printf("Done\n");
}
