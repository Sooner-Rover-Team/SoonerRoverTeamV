// Run on nucleo
#include "mbed.h"
// imported from https://os.mbed.com/users/tecnosys/code/mcp2515/
#include "CAN3.h"
#include "Servo.h"
#include "math.h"

SPI spi(A6,A5,A4);

CAN3 can(spi, A3, A2);

DigitalOut led(LED1);

Servo motor(D9);

int main() {
    can.frequency(8000000);
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
        
        float motor_speed = 0.0;
        bool negative_speed = false;
        for (size_t i = 0; i < 6; i++) {
            char speed = c_msg.data[i];
            if (speed == '-') {
                negative_speed = true;
                continue;
            }
            speed = speed - '0';
            motor_speed += speed * pow(10.0, (double) 5 - i);
        }
        
        if (negative_speed) {
            motor_speed *= -1.0f;
        }
        
        motor_speed += 126.0f;
        if (motor.read() != motor_speed / 252.0f) {
            motor.write(motor_speed / 252.0f);
        }
        
        wait(.1);
        led = 0;
    }
}