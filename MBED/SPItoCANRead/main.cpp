// Run on nucleo
#include "mbed.h"
// imported from https://os.mbed.com/users/tecnosys/code/mcp2515/
#include "CAN3.h"
#define VIRUS 0

#define LPC 0
#if LPC
SPI spi(p11,p12,p13);
CAN3 can(spi, p14, p10);
#else
SPI spi(A6,A5,A4);
CAN3 can(spi, A3, A2);
#endif

DigitalOut led(LED1);
CANMessage c_msg;
uint8_t status;

int main() {
    can.frequency(CAN_125KBPS_8MHZ);
    wait(.1);
    //char c = 0;
    led = 0;
    int sum = 0;
//    printf("did this work\r\n");
    can.read(&c_msg);
    can.read(&c_msg);
    while(1) {
        status = can.read(&c_msg);
        
        if (status == CAN_OK && c_msg.id == 1) {
            printf("msg received\r\n");
            printf("msg read\r\n");
            led = 1;
            sum = 0;
            for (size_t i = 0; i < 6; i++) {
                char speed = c_msg.data[i];
                sum += (unsigned char)speed;
                printf("wheel %d speed: %d, hex: %x\r\n",i,speed,speed);
            }
            sum &= 0xff;
            printf("cs: %d\r\n",sum);
            if (sum == c_msg.data[6]) {
                printf("%d checks out\r\n", sum);
            } else {
                printf("%d != %d\r\n", sum, c_msg.data[7]);
            }
        } else if (status == CAN_NOMSG) {
            led = 0;
//            printf("st: %d\r\n", status);
            wait(.05);
        }
    }
}
