// Run on nucleo
// imported by default
#include "mbed.h"
// imported from https://os.mbed.com/users/tecnosys/code/mcp2515/
#include "CAN3.h"
// imported from https://os.mbed.com/users/simon/code/Servo/
#include "Servo.h"

// debug print, turn this off because it's slow
#define DEBUG 0
#define dbprint(fmt, ...) do {if (DEBUG) printf(fmt, __VA_ARGS__); } while (0);

// autostop is one second
#define AUTOSTOP 1.0
// hard code the wheel number to the MBED
#define WHEEL_NUM 0

// SPI for CAN object
SPI spi(A6,A5,A4);

// CAN object for talking to MCP2515
CAN3 can(spi, A3, A2);

// Motor for motor
Servo motor(D9);

// Timeout for automatically stopping the motors after a specified time
Timeout autostop, blink;

// LED
DigitalOut led(D13);

// Function to stop motor
void stopWheel() {
    motor = .5f;
}

// blink callback
void blinkLED() {
    led = 0;
}

int main() {
    // 8 MHz frequency
    can.frequency(8000000);
    // set motor to off
    motor = .5f;
    float speeds[6];
    // CAN message struct
    CANMessage c_msg;
    wait(.1);
    // discard the first two can messages read, i don't know
    // why but this is necessary if you don't want the wheels to
    // start moving in random directions
    can.read(&c_msg);
    can.read(&c_msg);
    while(1) {
        // if theres no message do nothing
        if (can.checkReceive() == CAN_NOMSG) continue;
        // blink LED if there is a message
        led = 1;
        blink.attach(&blinkLED,.1f);
        // read the CAN message
        can.read(&c_msg);
        int sum = 0;
        // calculate checksum and convert to motor format
        for (size_t i = 0; i < 6; i++) {
            char speed = c_msg.data[i];
            sum += speed;
            speeds[i] = speed / 252.0;
//            dbprint("wheel %d speed: %d, hex: %x\r\n",i+1,speed,speed);
        }
//        dbprint("wheel %d speed: %d\r\n",WHEEL_NUM,speeds[WHEEL_NUM]);
        sum &= 0xff;
        // commented out because the code literally would not compile
        // because of size
//        if (sum == //c_msg.data[7]) {
//            dbprint("checksum verified: %x\r\n",sum);
//        } else {
//            dbprint("checksum failed: sum: %x, data: %x\r\n",sum,c_msg.data[7]);
//        }
        // set motor speed if it is different
        if (motor != speeds[WHEEL_NUM]) {
            dbprint("setting wheel speed to %f\r\n",speeds[WHEEL_NUM]*2-1);
            motor = speeds[WHEEL_NUM];
        }
        // stop the wheel after 1 second
        autostop.attach(&stopWheel,AUTOSTOP);
    }
}