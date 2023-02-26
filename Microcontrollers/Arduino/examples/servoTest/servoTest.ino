#include <RobotLib.h>
#include <Servo.h>

// Declare objects for the servos
Servo servo1;
//Servo servo2;

// create names for the controller pins
//int control1 = A0;

// variables for the servo angle
int angle1;
int oldAngle = 90;
bool stopped = false;


// setup the servos by attaching the objects to the arduino pins
void setup() {
  Serial.begin(9600);
  servo1.attach(6, 900, 2100); // min/max in microseconds, 900-2100
  servo1.write(90);
  //pinMode(2, OUTPUT);
  //pinMode(3, OUTPUT);

}


void loop() 
{ 
  
 Serial.println("Input 0-180 to control the angle of the servo1");
 // get the value the user inputs
 while (Serial.available() == 0) {}// this waits for someone to press enter with text in the Serial input.
 String userInput1 = Serial.readString(); // read the text (given by the user) as a String object.
 int angle1 = userInput1.toInt(); // convert the String into an int (integer) variable.
 Serial.println(angle1); // print the number to the Serial Monitor. (used for debugging)

//  if(angle1 == 0) { // out
//    digitalWrite(2, HIGH);
//    digitalWrite(3, LOW);
//  }
//  else if(angle1 == 2) { // in
//   digitalWrite(2, LOW);
//   digitalWrite(3, HIGH);
//  }
//  else {
//    digitalWrite(2, HIGH);
//    digitalWrite(3, HIGH);
//  }

  // send the angle position to the servo
  // for(int i=0; i<180; i+=30) {
  //   servo1.write(i);
  //   delay(500);
  // }
  // for(int i=180; i>0; i-=30) {
  //   servo1.write(i);
  //   delay(500);
  // }
  if(angle1 != oldAngle) {
    servo1.write(angle1);
    oldAngle = angle1;
  }
  //servo2.write(angle2);
  delay(1000);
}
