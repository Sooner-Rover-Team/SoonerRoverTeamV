// Run on nucleo
#include "mbed.h"
// imported from https://os.mbed.com/users/tecnosys/code/mcp2515/
#include "CAN3.h"
// used for random
#include <stdlib.h>

#define LPC 1
#if LPC
SPI spi(p11,p12,p13);
CAN3 can(spi, p14, p15);
#else
SPI spi(A6,A5,A4);
CAN3 can(spi, A7, A2);
#endif
DigitalOut led(LED1);

int main() {
    can.frequency(CAN_125KBPS_8MHZ);
    char data[8];
    time_t t;
    srand((unsigned)time(&t));
    int sum = 0;
    while(1) {
        led = 1;
        sum = 0;
        for (size_t i = 0; i < 6; i++) {
            char speed = (i == 0) ? (rand() % 127) : (rand() % 253);
            printf("wheel %d speed: %d\r\n",i,speed);
            data[i] = speed;
            sum += (int)speed;
        }
        sum &= 0xff;
        printf("cs: %d\r\n",sum);
        data[6] = sum;
        CANMessage c_msg(1, data, 7, CANData, CANStandard);
        can.write(&c_msg);
        wait(.1);
        led = 0;
        wait(.9);
    }
}
