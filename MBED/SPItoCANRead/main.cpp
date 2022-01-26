// Run on nucleo
#include "mbed.h"
// imported from https://os.mbed.com/users/tecnosys/code/mcp2515/
#include "CAN3.h"

SPI spi(A6,A5,A4);

CAN3 can(spi, A3, A2);

DigitalOut led(LED1);

int main() {
    can.frequency(8000000);
    char c = 0;
    led = 0;
    while(1) {
        CANMessage c_msg;
        while (can.checkReceive() == CAN_NOMSG) {
            }
        can.read(&c_msg);
        led = 1;
        for (size_t i = 0; i < 6; i++) {
            char speed = c_msg.data[i];
            printf("wheel %d speed: %d, hex: %x\r\n",i+1,speed,speed);
        }
        can.reset();
        wait(.1);
        led = 0;
    }
}