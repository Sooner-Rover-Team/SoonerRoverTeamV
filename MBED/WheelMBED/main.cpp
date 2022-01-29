// Run on nucleo
// imported by default
#include "mbed.h"
// imported from https://os.mbed.com/users/tecnosys/code/mcp2515/
#include "CAN3.h"
// imported from https://os.mbed.com/users/simon/code/Servo/
#include "Servo.h"

#define DEBUG 1
#define dbprint(fmt, ...) do {if (DEBUG) printf(fmt, __VA_ARGS__); } while (0);

#define AUTOSTOP 5.0
#define WHEEL_NUM 0

// SPI for CAN object
SPI spi(A6,A5,A4);

// CAN object for talking to MCP2515
CAN3 can(spi, A3, A2);

// Motor for motor
Servo motor(D9);

// Timeout for automatically stopping the motors after a specified time
Timeout autostop;

// Function to stop motor
void stopWheel() {
    motor = .5f;
    dbprint("5 seconds have passed, stopping wheel\r\n",0);
}

int main() {
    // 8 MHz frequency
    can.frequency(8000000);
    motor = .5f;
    float speeds[6];
    CANMessage c_msg;
    wait(.1);
    can.read(&c_msg);
    can.read(&c_msg);
    while(1) {
        if (can.checkReceive() == CAN_NOMSG) continue;
        can.read(&c_msg);
        int sum = 0;
        for (size_t i = 0; i < 6; i++) {
            char speed = c_msg.data[i];
            sum += speed;
            speeds[i] = speed / 252.0;
            dbprint("wheel %d speed: %d, hex: %x\r\n",i+1,speed,speed);
        }
        sum &= 0xff;
        if (sum == c_msg.data[7]) {
            dbprint("checksum verified: %x\r\n",sum);
        } else {
            dbprint("checksum failed: sum: %x, data: %x\r\n",sum,c_msg.data[7]);
        }
        
        if (motor != speeds[WHEEL_NUM]) {
            dbprint("setting wheel speed to %f\r\n",speeds[WHEEL_NUM]*2-1);
            motor = speeds[WHEEL_NUM];
        }
        autostop.attach(&stopWheel,AUTOSTOP);
    }
}