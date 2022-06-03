// Run on nucleo
// imported by default
#include "mbed.h"
// imported from https://os.mbed.com/users/tecnosys/code/mcp2515/
#include "CAN3.h"
// imported from https://os.mbed.com/users/simon/code/Servo/
#include "Servo.h"

// debug print, turn this off because it's slow
#define DEBUG 1

// autostop is one second
#define AUTOSTOP 1.0
// hard code the wheel number to the MBED
#define WHEEL_NUM 0

#define LPC 0
#if LPC
SPI spi(p11,p12,p13);
CAN3 can(spi, p14, p15);
Servo motor(p24);
DigitalOut led(LED1);
#else
SPI spi(A6,A5,A4);
CAN3 can(spi, A3, A2);
// Servo for motor
Servo motor(D9);
// LED
DigitalOut led(D13);
#endif


// Timeout for automatically stopping the motors after a specified time
Timeout autostop;
//Timeout blink;

CANMessage c_msg;
float speeds[6];
uint8_t status;
//Kernel::Clock::time_point timeout = Kernel::Clock::now();

// Function to stop motor
void stopWheel() {
    motor = .5f;
    #if DEBUG
    printf("wheels stopped\r\n");
    #endif
}

// blink callback
//void blinkLED() {
//    led = 0;
//}


int main() {
    // 8 MHz frequency
    can.frequency(8000000);
//    #if DEBUG
//    printf("freq set\r\n");
//    #endif
    // set motor to off
    motor = .5f;
    // CAN message struct
//    CANMessage c_msg;
    wait(.1);
    // discard the first two can messages read, i don't know
    // why but this is necessary if you don't want the wheels to
    // start moving in random directions
    can.read(&c_msg);
    can.read(&c_msg);
//    #if DEBUG
//    printf("first 2 messages thrown away\r\n");
//    #endif
    int sum = 0;
    while(1) {
        status = can.read(&c_msg);
        
        if (status == CAN_OK) {
            led = 1;
//            blink.attach(&blinkLED,.1f);
            // read the CAN message
            sum = 0;
            // calculate checksum and convert to motor format
            for (size_t i = 0; i < 6; i++) {
                char speed = c_msg.data[i];
                sum += (unsigned char)speed;
                if (i == 0) {
                    speeds[i] = speed / 126.0;
                } else {
                    speeds[i] = speed / 252.0;
                }
                #if DEBUG
                printf("%d: %d, ",i+1,speed);
                #endif
            }
            #if DEBUG
            printf("\r\n");
            #endif
        //        dbprint("wheel %d speed: %d\r\n",WHEEL_NUM,speeds[WHEEL_NUM]);
            sum &= 0xff;
            // commented out because the code literally would not compile
            // because of size
            if (sum == c_msg.data[6]) {
                // set motor speed if different
                #if DEBUG
                printf("cs: %x\r\n",sum);
                #endif
                if (motor != speeds[WHEEL_NUM]) {
                    #if DEBUG
                    printf("sp:%f\r\n",speeds[WHEEL_NUM]*2-1);
                    #endif
                    if (WHEEL_NUM == 4) 
                        speeds[WHEEL_NUM] = 1-speeds[WHEEL_NUM];
                    motor = speeds[WHEEL_NUM];
                    
                }
                autostop.attach(&stopWheel,AUTOSTOP);
            } else {
                #if DEBUG
                printf("badcs: %x, %x\r\n",sum,c_msg.data[6]);
                #endif
            }
            // stop the wheel after 1 second
            
        } else if (status == CAN_NOMSG) {
            led = 0;
            wait(.01);
        }
    }
}
