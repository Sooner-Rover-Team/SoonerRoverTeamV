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
// define a static ip, the netmask, and the gateway (router's ip addr)
#define IP_ADDR "10.0.0.101"
#define NETMASK "255.255.255.0"
#define GATEWAY "10.0.0.1"
// define MAC address, can be anything as long as it is unique
unsigned char MAC_ADDR[6] = {0xa2, 0x41, 0x12, 0x02, 0xb3, 0xff};

// toggle debug print statements
// set this to 0 when using because the print
// statements cause latency
#define DEBUG 1

// Network interface
EthernetInterface net;

// SPI definition
SPI spi(p11,p12,p13);

// LED to indicate if MBED is reachable by internet
DigitalOut con_LED(LED1);
// LED to indicate if a msg has been received
DigitalOut msg_LED(LED2);
// LED to indicate if the wheels are currently enabled
DigitalOut whl_LED(LED3);

// Control the LED strip
PwmOut red(p26), blue(p24), green(p25);

// Timeout for blinking and reseting wheels (not implemented yet)
Timeout blink, wheelreset;

// Chip Select
DigitalOut cs1(p14);

// Control relay for wheel power in E box
DigitalOut relay(p16);

// CAN interface
CAN3 can(spi, p14, p15);

// callback to turn msg_LED off
void LEDOff() {
    msg_LED = 0;
}

// calculate 8bit checksum of an array
char get_cs(char * arr, int length) {
    int cs = 0;
    for (int i = 0; i < length; i++) {
        cs += (int)arr[i];
    }
    cs &= 0xff;
    return cs;
}

// send the wheel speeds over CAN
void sendWheelSpeeds(char *speeds) {
    speeds[0] /= 2;
    char cs = get_cs(speeds, 6);
    speeds[6] = cs;
    if (DEBUG) printf("can cs: %d\n",speeds[6]);
    CANMessage c_msg(1, speeds, 7, CANData, CANStandard);
    can.write(&c_msg);
    if (DEBUG) printf("CANsent\n");
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
    whl_LED = !whl_LED;
}

// sets LEDstrip to specified RGB value
void setLEDStrip(char r, char g, char b) {
    red = (r/255.0);
    green = (g/255.0);
    blue = (b/255.0);
    if (DEBUG) printf("r: %d g: %d b: %d\r\n",r,g,b);
}


int main()
{
    // turn off all LEDS
    con_LED = 0;
    relay = 0;
    msg_LED = 0;
    whl_LED = 1;
    // set PWM period
    red.period(0.001);
    green.period(0.001);
    blue.period(0.001);
    red = 0;
    green = 0;
    blue = 0;
    
    // set CAN frequency to 8 MHz
    can.frequency(8000000);
    
    // set the static IP and MAC address
    net.set_network(IP_ADDR,NETMASK,GATEWAY);
    net.set_mac_address(MAC_ADDR,6);
    // start the ethernet interface
    if (DEBUG) printf("Setting up UDP Socket over ethernet\n");
    net.connect();

    // Show the network address
    SocketAddress a;
    net.get_ip_address(&a);
    while(!a.get_ip_address()) {
        net.get_ip_address(&a);
    }
    if (DEBUG) {
        printf("IP address: %s\n", a.get_ip_address() ? a.get_ip_address() : "None");
        printf("MAC address: %s\n", net.get_mac_address());
    }
    if (a.get_ip_address())
        con_LED = 1;
    

    // Open a socket on the network interface
    UDPSocket socket;
    socket.open(&net);
    // Listen on port 80
    socket.bind(PORT);
    
    // create variables for holding data
    char data[9];
    char speeds[7];
    char stopmsg = 0;
    while (1) {
        // receive the data
        int size = socket.recv(data,PORT);
        // if the message start is correct
        if (data[0] == startbyte) {
            if (DEBUG) printf("start\n");
            if (data[1] == 0x00) {
                if (DEBUG) printf("wheelmsg\n");
                // checksum
                if (DEBUG) printf("[");
                for (int i = 2; i < 8; i++) {
                    if (DEBUG) printf("%d",data[i]);
                    if (DEBUG && i != 7) printf(", ");
                    speeds[i-2] = data[i];
                }
                if (DEBUG) printf("]\n");
                // calc checksum
                int checksum = get_cs(speeds, 6);
                // if it was good
                if (data[8] == checksum) {
                    if (DEBUG) printf("csgood: %x\n",checksum);
                    // only send a stop message one time (helps with latency)
                    if (isStop(speeds)) {
                        if (!stopmsg) {
                            sendWheelSpeeds(speeds);
                            stopmsg = 1;
                            msg_LED = 1;
                            if (DEBUG) printf("stp sent\n");
                        }
                    // send a drive message repeatedly until we no longer
                    // wish to drive
                    } else {
                        sendWheelSpeeds(speeds);
                        stopmsg = 0;
                        msg_LED = 1;
                        if (DEBUG) printf("spd sent\n");
                    }
                    blink.attach(&LEDOff, 200ms);

                }
                // uh oh check sum bad
                else
                    if (DEBUG) printf("csbad: %d, d8: %d\n",checksum,data[8]);
            }
            // message to toggle the wheels
            else if (data[1] == 0x01) {
                if (DEBUG) printf("wheeltg\n");
                toggleWheels();
            }
            // message to set the LEDStrip
            else if (data[1] == 0x02) {
                if (DEBUG) printf("LEDmsg\n");
                setLEDStrip(data[2],data[3],data[4]);
            }
        }
        // set data buffer to 0
        memset(data, 0, sizeof(data));
    }

    // Close the socket to return its memory and bring down the network interface
    socket.close();

    // Bring down the ethernet interface
    net.disconnect();
    if (DEBUG) printf("Done\n");
}
