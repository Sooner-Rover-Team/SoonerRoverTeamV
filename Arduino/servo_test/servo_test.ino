#include <Servo.h>

// This basic tool can be used to test and calibrate the talons.
// Talons should be calibrated to the range 10-170. They freak out if you go below 10 or above 170

#define PIN_SERVO A3

String inString = "";
Servo myServo;

void setup() {
  Serial.begin(9600);
  Serial.println("Enter values 0 < x < 180.");
  
  myServo.attach(PIN_SERVO);
  myServo.write(90);
}

void loop() {
  while (Serial.available() > 0)
  {
    int inChar = Serial.read();
    if (isDigit(inChar))
      inString += (char)inChar;
    
    if (inChar == '\n')
    {
      int temp = inString.toInt();
      inString = "";

      Serial.println(temp);
      myServo.write(temp);
    }
  }
  delay(5);
}
