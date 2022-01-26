// Run on nucleo
#include "mbed.h"
// imported from https://os.mbed.com/users/tecnosys/code/mcp2515/
#include "CAN3.h"
// used for random
#include <stdlib.h>

DigitalOut led(LED1);

SPI spi(A6,A5,A4);

CAN3 can(spi, A3, A2);

int main() {
    can.frequency(8000000);
    char data[8];
    time_t t;
    srand((unsigned)time(&t));
    while(1) {
        led = 1;
        for (size_t i = 0; i < 6; i++) {
            char speed = (rand() % 253);
            printf("wheel %d speed: %d\r\n",i+1,speed);
            data[i] = speed;
        }
        CANMessage c_msg(1, data, 8, CANData, CANStandard);
        can.write(&c_msg);
        wait(.1);
//        printf("sent %d\r\n",c);
        led = 0;
        wait(.9);
    }
}