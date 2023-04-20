#include <Servo.h>

/*
 * NANO PWM pins: D3, D5, D6, D9, D10, D11
 * 
 * PINS USED BY ETHERNET SHEILD: D10, D11, D12, D13 (it uses SPI)
 * 
 * USING TALONS TO CONTROL ALL MOTORS (ACTYUATOR/CAROUSEL) -> TREAT EACH MOTOR AS A CONTINUOUS SERVO
 *  The carousel and linear actuator are going to have external limit switches to monitor their positions.
 * 
 * LINEAR ACTUATOR - D2/D3
 * CAROUSEL - D5
 *  - limit switch - A4

 * FAN - D6
 * MICROSCOPE - D7/D8
 *    - encoder - A5
 */

// Set equal to 1 for serial debugging
#define DEBUG 1

// Note: analogWrite() can not be used on pins 9 or 10 because of the servo library.
// Servos can still be used on those pins though
#define ACTUATOR_UP_PIN 2 // which pin is up depends on wiring. Can be reversed
#define ACTUATOR_DOWN_PIN 3

#define CAROUSEL_PIN 5
#define CAROUSEL_LIMIT_PIN A4

#define FAN_PIN 6
#define MICROSCOPE_UP_PIN 7
#define MICROSCOPE_DOWN_PIN 8
#define MICROSCOPE_ENCODER_PIN A5

// servo objects for talon motor controllers
Servo carousel, fan;

// raw bytes to store from ethernet data
// they are converted to output ranges in updateServos()
int linearActuatorSpeed = 127;
int carouselSpeed = 1;
int fanSpeed = 90;
int microscopePosition = 1;

bool carouselMoving = false;
bool linearActuatorMoving = false;

unsigned long stopTimeout = 0, turnTimeout = 0;


void setup()
{
  // setup motors
  pinMode(ACTUATOR_UP_PIN, OUTPUT);
  pinMode(ACTUATOR_DOWN_PIN, OUTPUT);
  digitalWrite(ACTUATOR_UP_PIN, LOW);
  digitalWrite(ACTUATOR_DOWN_PIN, LOW);
  pinMode(MICROSCOPE_UP_PIN, OUTPUT);
  pinMode(MICROSCOPE_DOWN_PIN, OUTPUT);
  digitalWrite(MICROSCOPE_UP_PIN, LOW);
  digitalWrite(MICROSCOPE_DOWN_PIN, LOW);

  carousel.attach(CAROUSEL_PIN, 900, 2100);
  fan.attach(FAN_PIN, 900, 2100);
  // all motors should start in neutral position (resting for motors, 90 degrees for servos)
  carousel.write(90);
  fan.write(90);

  pinMode(CAROUSEL_LIMIT_PIN, INPUT_PULLUP); // digital signal
  pinMode(MICROSCOPE_ENCODER_PIN, INPUT); // analog signal


  Serial.begin(9600);
  #if DEBUG
    Serial.begin(9600);
  #endif

}

String input;

void loop()
{
  Serial.println("Enter device to control:");
  Serial.println("A: Actuator");
  Serial.println("B: Carousel");
  Serial.println("C: Fan");
  Serial.println("D: Microscope");
  while (Serial.available() == 0) {}
  input = Serial.readString();
  input.toUpperCase();
  char choice = input[0];

  switch (choice) { 
    case 'A':
      while (true) {
        Serial.println("[U]p, [D]own, [S]top, [Q]uit");
        while (Serial.available() == 0) {}
        input = Serial.readString();
        input.toUpperCase();
        if (input[0] == 'S' || input[0] == 'Q') {
          digitalWrite(ACTUATOR_UP_PIN, LOW);
          digitalWrite(ACTUATOR_DOWN_PIN, LOW);
          if (input[0] == 'Q') break;
        } 
        else if (input[0] == 'D') {
          digitalWrite(ACTUATOR_DOWN_PIN, HIGH);
        } 
        else if (input[0] == 'U') {
          digitalWrite(ACTUATOR_UP_PIN, HIGH);
        }
      }
      break;
    case 'B':
     while (true) {
        Serial.println("[L]eft, [R]ight, [Q]uit");
        while(Serial.available() == 0) {}
        input = Serial.readString();
        input.toUpperCase();
        if (input[0] == 'Q') {
          carousel.write(90);
          break;
        }
        else if (input[0] == 'L') {
          Serial.println("carousel left");
          carousel.write(130);
          carouselMoving = true;
        } else if (input[0] == 'R') {
          carousel.write(50);
          carouselMoving = false;
        }
        delay(200);
        while (digitalRead(CAROUSEL_LIMIT_PIN)) {}
        carousel.write(90);
        carouselMoving = false;
     }
     case 'C':
      while (true) {
        Serial.println("Speed (0-180), [Q]uit");
        while (Serial.available() == 0) {}
        input = Serial.readString();
        input.toUpperCase();
        if (input[0] == 'Q') {
          fan.write(90);
          break;          
        }
        else {
          fanSpeed = input.toInt();
          if (fanSpeed <= 180 && fanSpeed >= 0) {
            fan.write(fanSpeed);
          }
          else {
            Serial.println("Input out of range.");
            fan.write(90);
          }
        }
      }
      break;
    case 'D':
      while (true) {
        Serial.println("[U]p, [D]own, [Q]uit");
        while (Serial.available() == 0) {}
        input = Serial.readString();
        input.toUpperCase();
        if (input[0] == 'Q') {
          digitalWrite(MICROSCOPE_UP_PIN, LOW);
          digitalWrite(MICROSCOPE_DOWN_PIN, LOW);
          break;
        }
        else if (input[0] == 'U') {
          digitalWrite(MICROSCOPE_UP_PIN, HIGH);
        }
        else if (input[0] == 'D') {
          digitalWrite(MICROSCOPE_DOWN_PIN, HIGH);
        }
      }
      break;
  }
  delay(10);
}