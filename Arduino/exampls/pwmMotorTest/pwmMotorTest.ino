
 /*
 * This is Arduino Sketch for Tutorial video 
 * explaining why resistor is needed to be used with push button
 * with Arduino to connect the pin to Ground (GND)
 * 
 * Written by Ahmad Shamshiri on July 18, 2018 at 17:36 in Ajax, Ontario, Canada
 * For Robojax.com
 * Watch instruction video for this code: https://youtu.be/tCJ2Q-CT6Q8
 * This code is "AS IS" without warranty or liability. Free to be used as long as you keep this note intact.
 */
int motorPin =6;// pin to connect to motor module
int motorPin1 =5;
int mSpeed = 0;// variable to hold speed value
int mStep = 15;// increment/decrement step for PWM motor speed
  
void setup() {
  // Robojax.com demo
  pinMode(motorPin,OUTPUT);// set mtorPin as output
  pinMode(motorPin1, OUTPUT);
  Serial.begin(9600);// initialize serial motor
  Serial.println("Robojax Demo");
  

}

void loop() {
  // Robojax.com  tutorial
   Serial.println("Input 0-99 to control the motor");
  // get the value the user inputs
  while (Serial.available() == 0) {}// this waits for someone to press enter with text in the Serial input.
  String userInput1 = Serial.readString(); // read the text (given by the user) as a String object.
  int mSpeed = userInput1.toInt(); // convert the String into an int (integer) variable.
  Serial.println(mSpeed); // print the number to the Serial Monitor. (used for debugging)

  if(mSpeed < 50) {
    analogWrite(motorPin1, 0);
    analogWrite(motorPin, map(mSpeed, 0, 49, 0, 255));// send mSpeed value to motor
  }
  else {
    analogWrite(motorPin, 0);
    analogWrite(motorPin1, map(mSpeed, 50, 999, 0, 255));// send mSpeed value to motor
  }
  
delay(200);

} 