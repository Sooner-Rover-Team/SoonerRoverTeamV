#include <Ethernet.h>
#include <EthernetUdp.h>
#include <Servo.h>
#include "PID.h"

// "PID.h" is a modified version of Brett Beauregard's PID Library (see links below).
// https://playground.arduino.cc/Code/PIDLibrary/
// https://github.com/br3ttb/Arduino-PID-Library/
// All I did was add a function to reset the integral term.

// Advanced PID Rover Arm Tester (incomplete)
// Written for the Arduino Mega on the rover's arm
// Open the serial monitor to use

// This program lets you set manually set the position of each joint.
// Talons should be calibrated to the range of servo inputs 10-170.
// A position of 0 encoder ticks should be the default position.

// Caution: This code will not stop you from breaking the arm


// TODO: communication timeout
// TODO: figure out whether or not the program is crashing
// TODO: (not urgent) Increase precision of encoders

// need to test: actually using doubles for the PID stuff (improves accuracy)
//               limited max joint speed (by changing PID bounds)


// Arduino Mega pins to attach Talon controllers to
#define PIN_S_BASE 30
#define PIN_S_SHOULDER 31
#define PIN_S_ELBOW 32
#define PIN_S_CLAW 33
#define PIN_S_WRISTP 34
#define PIN_S_WRISTR 35

// Arduino Mega pins to attach limit switches to
#define PIN_L_BASE 36
#define PIN_L_SHOULDER_MIN 37
#define PIN_L_SHOULDER_MAX 38
#define PIN_L_ELBOW_MIN 39
#define PIN_L_ELBOW_MAX 40
#define PIN_L_WRISTP_MIN 41 // unused?
#define PIN_L_WRISTP_MAX 42 // unused?
#define PIN_L_CLAW 43

// Port K bits (pins) for encoders
#define ENC_BASE_A 0x01     // pin A8
#define ENC_BASE_B 0x02     // pin A9
#define ENC_SHOULDER_A 0x04 // pin A10
#define ENC_SHOULDER_B 0x08 // pin A11
#define ENC_ELBOW_A 0x10    // pin A12
#define ENC_ELBOW_B 0x20    // pin A13
#define ENC_WRISTP_A 0x40   // pin A14
#define ENC_WRISTP_B 0x80   // pin A15

// Encoder position limits
#define MIN_BASE -500          // update this!
#define MAX_BASE 500           // update this!
#define MIN_SHOULDER 0
#define MAX_SHOULDER 1100
#define MIN_ELBOW 0
#define MAX_ELBOW 310
#define MIN_WRISTP -278
#define MAX_WRISTP 295

// Offset of the setpoint for the PID controls during the zeroing process
#define ZERO_SPEED 10
// Time (ms) between changing encoder position
#define ZERO_PERIOD 500
#define DEBUG_PERIOD 750

#define PID_MAP_SERVO 255 // "PID range." If you change this, then you'll have to retune all PID loops
#define PID_LIMIT 200 // setting PID_LIMIT < PID_MAP_SERVO will cap the PID speeds w/o changing tuning

#define JOY_DEADZONE 20
#define JOY_MAX 863
#define JOY_ZERO 429
#define JOY_MIN 0

#define DEVICE_ID 1

// encoder positions - updated by interrupt
volatile int eBase = 0;
volatile int eShoulder = 0;
volatile int eElbow = 0;
volatile int eWristP = 0;
volatile byte port_k_prev = 0x00; // only used by ISR

// servo objects
Servo sBase;
Servo sShoulder;
Servo sElbow;
Servo sClaw;
Servo sWristP;
Servo sWristR;

// PID stuff
double pidSetBase, pidInBase, pidOutBase;
PID pidBase(&pidInBase, &pidOutBase, &pidSetBase, 1, 1, 0, P_ON_E, REVERSE); // numbers are P, I, D

double pidSetShoulder, pidInShoulder, pidOutShoulder;
PID pidShoulder(&pidInShoulder, &pidOutShoulder, &pidSetShoulder, 1, 1, 0, P_ON_E, REVERSE); // numbers are P, I, D

double pidSetElbow, pidInElbow, pidOutElbow;
PID pidElbow(&pidInElbow, &pidOutElbow, &pidSetElbow, 1, 1, 0, P_ON_E, REVERSE); // numbers are P, I, D

double pidSetWristP, pidInWristP, pidOutWristP;
PID pidWristP(&pidInWristP, &pidOutWristP, &pidSetWristP, 1, 1, 0, P_ON_E, REVERSE); // numbers are P, I, D

// UDP Stuff
char message[30];  // buffer to hold incoming packet
int messageSize;
EthernetUDP Udp;
static byte mymac[] = { 0xAB, 0xCD, 0xEF, 0x01, 0x23, 0x45 };
IPAddress myip(192, 168, 1, 140);
const int localPort = 2040;

// test program vars
bool calibrated = true;
unsigned long timePrint, timeZero;
int jWristR;
bool bClawO, bClawC;


void setup() {
  // setup servos
  sBase.attach(PIN_S_BASE);
  sShoulder.attach(PIN_S_SHOULDER);
  sElbow.attach(PIN_S_ELBOW);
  sClaw.attach(PIN_S_CLAW);
  sWristP.attach(PIN_S_WRISTP);
  sWristR.attach(PIN_S_WRISTR);
  
  sBase.write(90);
  sShoulder.write(90);
  sElbow.write(90);
  sClaw.write(90);
  sWristP.write(90);
  sWristR.write(90);

  // setup encoder pins and interrupts
  cli();
  DDRK &= 0x00; // set encoder pins (all 8 port k bits) as inputs
  PORTK |= 0xFF; // enable pullups on encoder pins
  PCICR |= 0x04; // enable port K pin change interrupt
  PCMSK2 |= 0xFF; // enable interrupt for all port K pins
  sei();

  port_k_prev = PINK;

  // setup limit switch pins (uses pull up resistors)
  pinMode(PIN_L_BASE, INPUT);
  digitalWrite(PIN_L_BASE, HIGH);
  pinMode(PIN_L_SHOULDER_MIN, INPUT);
  digitalWrite(PIN_L_SHOULDER_MIN, HIGH);
  pinMode(PIN_L_SHOULDER_MAX, INPUT);
  digitalWrite(PIN_L_SHOULDER_MAX, HIGH);
  pinMode(PIN_L_ELBOW_MIN, INPUT);
  digitalWrite(PIN_L_ELBOW_MIN, HIGH);
  pinMode(PIN_L_ELBOW_MAX, INPUT);
  digitalWrite(PIN_L_ELBOW_MAX, HIGH);
  pinMode(PIN_L_WRISTP_MIN, INPUT);
  digitalWrite(PIN_L_WRISTP_MIN, HIGH);
  pinMode(PIN_L_WRISTP_MAX, INPUT);
  digitalWrite(PIN_L_WRISTP_MAX, HIGH);
  pinMode(PIN_L_CLAW, INPUT);
  digitalWrite(PIN_L_CLAW, HIGH);
  
  // setup serial
  Serial.begin(9600);
  
  // setup PID stuff
  pidBase.SetOutputLimits(-PID_LIMIT, PID_LIMIT);
  pidInBase = mapD(eBase, MIN_BASE, MAX_BASE, -PID_LIMIT, PID_LIMIT);
  pidSetBase = mapD(0, MIN_BASE, MAX_BASE, -PID_LIMIT, PID_LIMIT);
  pidBase.SetSampleTime(10);
  pidBase.SetMode(AUTOMATIC);

  pidShoulder.SetOutputLimits(-PID_LIMIT, PID_LIMIT);
  pidInShoulder = mapD(eShoulder, MIN_SHOULDER, MAX_SHOULDER, -PID_LIMIT, PID_LIMIT);
  pidSetShoulder = mapD(0, MIN_SHOULDER, MAX_SHOULDER, -PID_LIMIT, PID_LIMIT);
  pidShoulder.SetSampleTime(10);
  pidShoulder.SetMode(AUTOMATIC);

  pidElbow.SetOutputLimits(-PID_LIMIT, PID_LIMIT);
  pidInElbow = mapD(eWristP, MIN_ELBOW, MAX_ELBOW, -PID_LIMIT, PID_LIMIT);
  pidSetElbow = mapD(0, MIN_ELBOW, MAX_ELBOW, -PID_LIMIT, PID_LIMIT);
  pidElbow.SetSampleTime(10);
  pidElbow.SetMode(AUTOMATIC);

  pidWristP.SetOutputLimits(-PID_LIMIT, PID_LIMIT);
  pidInWristP = mapD(eWristP, MIN_WRISTP, MAX_WRISTP, -PID_LIMIT, PID_LIMIT);
  pidSetWristP = mapD(0, MIN_WRISTP, MAX_WRISTP, -PID_LIMIT, PID_LIMIT);
  pidWristP.SetSampleTime(10);
  pidWristP.SetMode(AUTOMATIC);

  // setup ethernet/udp
  Ethernet.init(10);
  Ethernet.begin(mymac, myip);
  if (Ethernet.hardwareStatus() == EthernetNoHardware) {
    Serial.println("Ethernet shield was not found.  Sorry, can't run without hardware. :(");
    while (true) {
      delay(1); // do nothing, no point running without Ethernet hardware
    }
  }
  if (Ethernet.linkStatus() == LinkOFF) {
    Serial.println("Ethernet cable is not connected.");
  }
  Udp.begin(localPort);
}

/*
 * When a mesage is available, stor it in message[].
 * Returns true if it's a valid control message, otherwise false.
 */
bool verify_message()
{
  // (-127), Device ID (1), base (high), base (low),
  // shoulder (high), shoulder (low), elbow (high), elbow (low),
  // wrist pitch (high), wrist pitch (low),
  // wrist roll (joystick high), wrist roll (joystick low),
  // buttons, hash

  messageSize = Udp.parsePacket();
  if (messageSize == 0)
    return false;
  
  Udp.read(message, messageSize);

  /*
  // DEBUG:
  for (int i = 0; i < messageSize: i++)
  {
    Serial.print((int)(message[i]));
    Serial.print(", ");
  }
  Serial.print("\n");
  */
  
  if(messageSize != 14)
  {
    Serial.println("Message is wrong length!");
    return false;
  }

  if(message[0] != -127)
  {
    Serial.println("Message does not start with -127!");
    return false;
  }

  if(message[1] != 1)
  {
    Serial.println("Wrong device id!");
    return false;
  }
  
  char hash = (message[2] + message[3] + message[4] + message[5] + message[6] + message[7] + message[8] + message[9] + message[10] + message[11] + message[12]) / 11;
  if(hash != message[13])
  {
    Serial.println("Wrong hash!");
    return false;
  }

  return true;
}

/*
 * Same function as the built in map(), except for a couple differences:
 * Uses doubles to give the PID controllers more precision
 * Limits the output to not go past out_min or out_max
 */
double mapD(double x, double in_min, double in_max, double out_min, double out_max) {
  //return (double(x)-double(in_min)) * (double(out_max) - double(out_min)) / (double(in_max) - double(in_min)) + double(out_min);
  double temp;
  temp = (x-in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
  if (temp > out_max)
    temp = out_max;
  else if (temp < out_min)
    temp = out_min;
  return temp;
}

/*
 * Sets all pid control setpoints and encoder positions to 0.
 * Stop motors.
 */
void pid_reset()
{
  sBase.write(90);
  eBase = 0;
  pidInBase = mapD(0, MIN_BASE, MAX_BASE, -PID_LIMIT, PID_LIMIT);
  pidSetBase = mapD(0, MIN_BASE, MAX_BASE, -PID_LIMIT, PID_LIMIT);
  pidBase.ResetI();
  
  sShoulder.write(90);
  eShoulder = 0;
  pidInShoulder = mapD(0, MIN_SHOULDER, MAX_SHOULDER, -PID_LIMIT, PID_LIMIT);
  pidSetShoulder = mapD(0, MIN_SHOULDER, MAX_SHOULDER, -PID_LIMIT, PID_LIMIT);
  pidShoulder.ResetI();

  sElbow.write(90);
  eElbow = 0;
  pidInElbow = mapD(0, MIN_ELBOW, MAX_ELBOW, -PID_LIMIT, PID_LIMIT);
  pidSetElbow = mapD(0, MIN_ELBOW, MAX_ELBOW, -PID_LIMIT, PID_LIMIT);
  pidElbow.ResetI();

  sWristP.write(90);
  eWristP = 0;
  pidInWristP = mapD(0, MIN_WRISTP, MAX_WRISTP, -PID_LIMIT, PID_LIMIT);
  pidSetWristP = mapD(0, MIN_WRISTP, MAX_WRISTP, -PID_LIMIT, PID_LIMIT);
  pidWristP.ResetI();
}

/*
 * Update pid controllers.
 * Handles limit switches.
 * Set motor speeds.
 * Doesn't change setpoints. 
 */
void pid_update()
{
  int temp;
  
  pidInBase = mapD(eBase, MIN_BASE, MAX_BASE, -PID_LIMIT, PID_LIMIT);
  pidBase.Compute();
  sBase.write(map(pidOutBase, -PID_MAP_SERVO, PID_MAP_SERVO, 10, 170));
  // TODO: limit switch(?)
  
  pidInShoulder = mapD(eShoulder, MIN_SHOULDER, MAX_SHOULDER, -PID_LIMIT, PID_LIMIT);
  pidShoulder.Compute();
  temp = map(pidOutShoulder, -PID_MAP_SERVO, PID_MAP_SERVO, 10, 170);
  if (digitalRead(PIN_L_SHOULDER_MIN) == LOW)
  {
    // limit switch pressed: reset position. don't let the motor move towards stow.
    eShoulder = MIN_SHOULDER;
    if (temp > 90)
      temp = 90;
  }
  if (digitalRead(PIN_L_SHOULDER_MAX) == LOW)
  {
    // limit switch pressed: reset position. don't let the motor move towards stow.
    eShoulder = MAX_SHOULDER;
    if (temp < 90)
      temp = 90;
  }
  sShoulder.write(temp);
  
  pidInElbow = mapD(eElbow, MIN_ELBOW, MAX_ELBOW, -PID_LIMIT, PID_LIMIT);
  pidElbow.Compute();
  temp = map(pidOutElbow, -PID_MAP_SERVO, PID_MAP_SERVO, 10, 170);
  if (digitalRead(PIN_L_ELBOW_MIN) == LOW)
  {
    // limit switch pressed: reset position. don't let the motor move towards stow.
    eElbow = MIN_ELBOW;
    if (temp > 90)
      temp = 90;
  }
  else if (digitalRead(PIN_L_ELBOW_MAX) == LOW)
  {
    // limit switch pressed: reset position. don't let the motor move towards stow.
    eElbow = MAX_ELBOW;
    if (temp < 90)
      temp = 90;
  }
  sElbow.write(temp);
  
  pidInWristP = mapD(eWristP, MIN_WRISTP, MAX_WRISTP, -PID_LIMIT, PID_LIMIT);
  pidWristP.Compute();
  sWristP.write(map(pidOutWristP, -PID_MAP_SERVO, PID_MAP_SERVO, 10, 170));
  // TODO: limit switch(?)
}

/* 
 * Moves all joints towards "zero" positions until the corresponding limit switch is pressed.
 * Needs to be called continuously until complete.
 * Currently only moves elbow and shoulder joints.
 */
void pid_zero() {
  // periodically add to encoder values to make joints move towards stow position.
  // set calibrated to true when complete
  if (millis()-timeZero > ZERO_PERIOD)
  {
    Serial.println("Zeroing...");
    timeZero = millis();
    calibrated = true;
    
    if (digitalRead(PIN_L_SHOULDER_MIN) == HIGH) // switch not pressed
    {
      eShoulder += ZERO_SPEED;
      calibrated = false;
    }

    if (digitalRead(PIN_L_ELBOW_MIN) == HIGH)
    {
      eElbow += ZERO_SPEED;
      calibrated = false;
    }
  }
}

void loop() {
  // periodically display encoder positions
  if (millis()-timePrint > DEBUG_PERIOD)
  {
    timePrint = millis();
    
    //Serial.println("set: " + String(pidSetShoulder) + "\tin: " + String(pidInShoulder) + "\tout: " + String(pidOutShoulder));
    
    /*
    Serial.print("B: " + String(pidSetBase) + ", " + String(pidOutBase));
    Serial.print("\tS: " + String(pidSetShoulder) + ", " + String(pidOutShoulder));
    Serial.print("\tE: " + String(pidSetElbow) + ", " + String(pidOutElbow));
    Serial.println("\tW: " + String(pidSetWristP) + ", " + String(pidOutWristP));
    */

    /*
    Serial.print("B: " + String(eBase));
    Serial.print("\tS: " + String(eShoulder));
    Serial.print("\tE: " + String(eElbow));
    Serial.println("\tW: " + String(eWristP));
    */
  }

  // update control variables when a message is received
  if (verify_message())
  {
    
    // DEBUG:
    for (int i = 0; i < messageSize; i++)
    {
      Serial.print((int)(message[i]));
      Serial.print(", ");
    }
    Serial.print("\n");
    

    double tempB, tempS, tempE, tempW;
    tempB = (double)((int)(message[2] << 8) + (byte)message[3]);
    tempS = (double)((int)(message[4] << 8) + (byte)message[5]);
    tempE = (double)((int)(message[6] << 8) + (byte)message[7]);
    tempW = (double)((int)(message[8] << 8) + (byte)message[9]);
    pidSetBase = mapD(tempB, MIN_BASE, MAX_BASE, -PID_LIMIT, PID_LIMIT);
    pidSetShoulder = mapD(tempS, MIN_SHOULDER, MAX_SHOULDER, -PID_LIMIT, PID_LIMIT);
    pidSetElbow = mapD(tempE, MIN_ELBOW, MAX_ELBOW, -PID_LIMIT, PID_LIMIT);
    pidSetWristP = mapD(tempW, MIN_WRISTP, MAX_WRISTP, -PID_LIMIT, PID_LIMIT);

    // wrist roll
    jWristR = ((int)(message[10] << 8) + (byte)message[11]);
    if (jWristR > JOY_MAX)
      jWristR = JOY_MAX;
    else if (jWristR < JOY_MIN)
      jWristR = JOY_MIN;
    if (jWristR > JOY_ZERO+JOY_DEADZONE)
      sWristR.write(map(jWristR, JOY_ZERO+JOY_DEADZONE, JOY_MAX, 90, 170));
    else if (jWristR < JOY_ZERO-JOY_DEADZONE)
      sWristR.write(map(jWristR, JOY_ZERO-JOY_DEADZONE, JOY_MIN, 90, 10));
    else
      sWristR.write(90);
    //Serial.println(sWristR.read());
      
  
    // open/close claw
    bClawO = (message[12] & 1);
    bClawC = ((message[12] >> 1) & 1);
    if (bClawO && !bClawC)
      sClaw.write(170);
    else if (bClawC && !bClawO)
      sClaw.write(10);
    else
      sClaw.write(90);
  }

  // update pid, motor outputs
  pid_update();

  if (!calibrated)
    pid_zero();
}

ISR(PCINT2_vect) // pin change interrupt for pins A8 to A15 (update encoder positions)
{
  byte port_k_pins = PINK;

  // base
  if ((port_k_pins & ENC_BASE_A) && !(port_k_prev & ENC_BASE_A)) // rising edge on A
  {
    if (port_k_pins & ENC_BASE_B)
      eBase--; // CCW
    else
      eBase++; // CW
  }
  else if (!(port_k_pins & ENC_BASE_A) && (port_k_prev & ENC_BASE_A)) // falling edge on A
  {
    if (port_k_pins & ENC_BASE_B)
      eBase++; // CW
    else
      eBase--; // CCW
  }

  // shoulder
  if ((port_k_pins & ENC_SHOULDER_A) && !(port_k_prev & ENC_SHOULDER_A)) // rising edge on A
  {
    if (port_k_pins & ENC_SHOULDER_B)
      eShoulder--; // CCW
    else
      eShoulder++; // CW
  }
  else if (!(port_k_pins & ENC_SHOULDER_A) && (port_k_prev & ENC_SHOULDER_A)) // falling edge on A
  {
    if (port_k_pins & ENC_SHOULDER_B)
      eShoulder++; // CW
    else
      eShoulder--; // CCW
  }

  // elbow
  if ((port_k_pins & ENC_ELBOW_A) && !(port_k_prev & ENC_ELBOW_A)) // rising edge on A
  {
    if (port_k_pins & ENC_ELBOW_B)
      eElbow--; // CCW
    else
      eElbow++; // CW
  }
  else if (!(port_k_pins & ENC_ELBOW_A) && (port_k_prev & ENC_ELBOW_A)) // falling edge on A
  {
    if (port_k_pins & ENC_ELBOW_B)
      eElbow++; // CW
    else
      eElbow--; // CCW
  }

  // wrist pitch
  if ((port_k_pins & ENC_WRISTP_A) && !(port_k_prev & ENC_WRISTP_A)) // rising edge on A
  {
    if (port_k_pins & ENC_WRISTP_B)
      eWristP--; // CCW
    else
      eWristP++; // CW
  }
  else if (!(port_k_pins & ENC_WRISTP_A) && (port_k_prev & ENC_WRISTP_A)) // falling edge on A
  {
    if (port_k_pins & ENC_WRISTP_B)
      eWristP++; // CW
    else
      eWristP--; // CCW
  }
  
  port_k_prev = port_k_pins;
}
