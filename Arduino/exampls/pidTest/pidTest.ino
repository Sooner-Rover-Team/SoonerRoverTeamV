/********************************************************
 * PID Basic Example
 * Reading analog input 0 to control analog PWM output 3
 ********************************************************/

#include <PID_v2.h>
#include <Encoder.h>
#include <Servo.h>

#define PIN_OUTPUT 6

Encoder encoder(2,3);
Servo servo;

// Specify the links and initial tuning parameters 2, 5, 1
double Kp = 2, Ki = 5, Kd = 0.2;
PID_v2 myPID(Kp, Ki, Kd, PID::Direct);

void setup() {

  servo.attach(PIN_OUTPUT, 900, 2100);
  Serial.begin(9600);

  Serial.println("PID with encoder test");

  pinMode(PIN_OUTPUT, OUTPUT);

  myPID.Start(encoder.read(),  // input
              0,                      // current output
              0);                   // setpoint
  myPID.SetOutputLimits(0, 180);
  myPID.SetControllerDirection(myPID.Reverse);
  Serial.println("PID started...");
}

void loop() {
  //const double input = encoder.read();
  long input = encoder.read();
  Serial.print("Encoder: ");
  Serial.println(input);
  const double output = myPID.Run(input);
  Serial.print("PID output: ");
  Serial.println(output);

  servo.write(int(output));
  //analogWrite(PIN_OUTPUT, output);
}
