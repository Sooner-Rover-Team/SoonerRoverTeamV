#include <Servo.h>

// Advanced Rover Arm Tester
// Written for the Arduino Mega on the rover's arm
// Open the serial monitor to use

// This program lets you set manually set the speed of each talon motor controller.
// Talons should be calibrated to the range of servo inputs 10-170, meaning 90 will be not moving.

// Caution: This code will not stop you from breaking the arm

// Arduino Mega pins to attach Talon controllers to
#define PIN_S_BASE 30
#define PIN_S_SHOULDER 31
#define PIN_S_ELBOW 32
#define PIN_S_CLAW 33
#define PIN_S_WRISTP 34
#define PIN_S_WRISTR 35

// Port K bits for encoders
#define ENC_BASE_A 0x01     // pin A8
#define ENC_BASE_B 0x02     // pin A9
#define ENC_SHOULDER_A 0x04 // pin A10
#define ENC_SHOULDER_B 0x08 // pin A11
#define ENC_ELBOW_A 0x10    // pin A12
#define ENC_ELBOW_B 0x20    // pin A13
#define ENC_WRISTP_A 0x40   // pin A14
#define ENC_WRISTP_B 0x80   // pin A15

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

// test program vars
String inString = "";
Servo* currentServo = &sElbow;
int ticks = 0;

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
  
  // setup serial
  Serial.begin(9600);
  
  Serial.println("Enter a number to set a speed:");
  Serial.println("90 is still (if motor controllers are calibrated).");
  Serial.println("Talon motor controllers should be calibrated to range of 10-170.");
  Serial.println();
  Serial.println("Enter a character to select motors:");
  Serial.println("A = base");
  Serial.println("B = shoulder");
  Serial.println("C = elbow (default)");
  Serial.println("D = claw");
  Serial.println("E = wrist pitch");
  Serial.println("F = wrist roll");
}

void loop() {
  // read and handle serial terminal commands
  while (Serial.available() > 0)
  {
    int inChar = Serial.read();
    if (inChar == '\n')
    {
      // check for number
      bool num = true;
      if (inString.length() == 0)
        num = false;
      for (int i = 0; i < inString.length(); i++)
      {
        if (!isDigit(inString[i]))
        {
          num = false;
          break;
        }
      }
      if (num)
      {
        // if a number, set the speed
        int temp = inString.toInt();
        Serial.println(temp);
        currentServo->write(temp);
      }
      else
      {
        // anything that isn't a number stops all servos (good for when you panic!)
        sBase.write(90);
        sShoulder.write(90);
        sElbow.write(90);
        sClaw.write(90);
        sWristP.write(90);
        sWristR.write(90);

        if (inString == "A" || inString == "a")
        {
          currentServo = &sBase;
          Serial.println("Selected Base");
        }
        else if (inString == "B" || inString == "b")
        {
          currentServo = &sShoulder;
          Serial.println("Selected Shoulder");
        }
        else if (inString == "C" || inString == "c")
        {
          currentServo = &sElbow;
          Serial.println("Selected Elbow");
        }
        else if (inString == "D" || inString == "d")
        {
          currentServo = &sClaw;
          Serial.println("Selected Claw");
        }
        else if (inString == "E" || inString == "e")
        {
          currentServo = &sWristP;
          Serial.println("Selected Wrist Pitch");
        }
        else if (inString == "F" || inString == "f")
        {
          currentServo = &sWristR;
          Serial.println("Selected Wrist Roll");
        }
        else
        {
          Serial.println("IDK what that means bro");
        }
      }

      inString = "";
    }
    else
    {
      // add character to string
      inString += (char)inChar;
    }
  }

  // periodically display encoder positions
  ticks++;
  if (ticks >= 100)
  {
    Serial.println("B " + String(eBase) + "\tS " + String(eShoulder) + "\tE " + String(eElbow) + "\tW " + String(eWristP));
    ticks = 0;
  }
  
  delay(10);
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
