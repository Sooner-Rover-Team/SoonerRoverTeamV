#include <Servo.h>
Servo servo;


/*
 * Servo library inputs numbers 0-180, which converts to PWM where 0 is the minimum Pulse-Width
 *    and 180 is the max Pulse-width. When using the Servo library with the Talon SRX, 
 *    servo.write(0) drive the motor full reverse, while servo.write(180) drives it forward and
 *    servo.write(90) stops the motor.
 *    
 *    
 * ALWAYS READ THE DATA SHEET OF A MOTOR CONTROLLER (Talon SRX) TO DETERMINE PWM INPUT
 * 
 * ALWAYS LOOK AT MICROCONTROLLER PIN-OUT TO DETERMINE WHICH PIN TO USE FOR PWM OUTPUT
 */


// setup the servos by attaching the objects to the arduino pins
void setup() {
  Serial.begin(9600); // Start up serial monitor
  Serial.println("starting");
  servo.attach(6, 1000, 2000); // configure servo object to output at pin 6

  servo.write(90); // stop motor at start-up

  pinMode(A7, OUTPUT);
  digitalWrite(A7, HIGH);
}


void loop() 
{ 
 // get new motor speed input from user
 Serial.println("Input 0-180 to control the angle of the servo1");
 // get the value the user inputs
 while (Serial.available() == 0) {}// this waits for someone to press enter with text in the Serial input.
 String userInput1 = Serial.readString(); // read the text (given by the user) as a String object.
 int angle1 = userInput1.toInt(); // convert the String into an int (integer) variable.
 Serial.println(angle1); // print the number to the Serial Monitor. (used for debugging)
 
 if((angle1 > 180) || (angle1 < 0)){ // if input is out of range, stop motor
  angle1 = 90;
 }

 servo.write(angle1); // generate the PWM signal
// delay(500); // pause code for half a second
}
