// daniel.j.fitzpatrick-1@ou.edu

// servo(90)
// servo(110) // retract
// servo(70)
#include <Servo.h>
Servo servo1, servo2, servo3;

// setup the servos by attaching the objects to the arduino pins
void setup() {
  Serial.begin(9600);
  Serial.println("starting");
  // pinMode(5, OUTPUT);
  // pinMode(6, OUTPUT);
  servo1.attach(6, 1000, 2000); // min/max in microseconds, 900-2100
  // servo2.attach(21, 1000, 2000);
  // servo3.attach(3, 1000, 2000);
  // servo1.write(90);
  // servo2.write(180);
  // servo3.write(170);

  // servo2.attach(5, 1000, 2000); // min/max in microseconds, 900-2100
  // servo2.write(119);
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

//  Serial.println("Input 0-180 to control the angle of the servo2");
//  // get the value the user inputs
//  while (Serial.available() == 0) {}// this waits for someone to press enter with text in the Serial input.
//  String userInput2 = Serial.readString(); // read the text (given by the user) as a String object.
//  int angle2 = userInput2.toInt(); // convert the String into an int (integer) variable.
//  Serial.println(angle2); // print the number to the Serial Monitor. (used for debugging)

//  if(angle1 == 0) { // out
//    digitalWrite(5, HIGH);
//    digitalWrite(6, LOW);
//  }
//  else if(angle1 == 2) { // in
//   digitalWrite(5, LOW);
//   digitalWrite(6, HIGH);
//  }
//  else {
//    digitalWrite(5, HIGH);
//    digitalWrite(6, HIGH);
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
  // if(angle1 != oldAngle) {
  //   servo1.write(angle1);
  //   oldAngle = angle1;
  // }
  servo1.write(angle1);
  //servo2.write(angle2);
  delay(500);
}
