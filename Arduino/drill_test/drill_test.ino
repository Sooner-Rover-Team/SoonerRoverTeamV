#include <Servo.h>

// Science package tester
// Currently can control the drill and fan

// Arduino Nano pins to attach Talon controllers to
#define PIN_S_1 6
#define PIN_S_2 7
#define PIN_ACTUATOR_UP 5
#define PIN_ACTUATOR_DOWN 3

// servo objects
Servo s1;
Servo s2;

// test program vars
String inString = "";
Servo* currentServo = &s1;
bool both = false;
bool actuator = false;

void setup() {
  // setup servos
  s1.attach(PIN_S_1);
  s2.attach(PIN_S_2);
  
  s2.write(90);
  s1.write(90);

  // Setup actuator control pins (analog outputs from range (-256, 256) with -256 being 12V to PIN_ACTUATOR_DOWN and 256 being 12V to PIN_ACTUATOR_UP)
  pinMode(PIN_ACTUATOR_UP, OUTPUT);
  pinMode(PIN_ACTUATOR_DOWN, OUTPUT);

  analogWrite(PIN_ACTUATOR_UP, 0);
  analogWrite(PIN_ACTUATOR_DOWN, 0);
  
  // setup serial
  Serial.begin(9600);

  Serial.println("Enter a number to set a speed:");
  Serial.println("90 is still (if motor controllers are calibrated).");
  Serial.println("Talon motor controllers should be calibrated to range of 10-170.");
  Serial.println();
  Serial.println("Enter a character to select motors:");
  Serial.println("A = Drill (> 90)");
  Serial.println("B = Fan (> 90)");
  Serial.println("C = Actuator");
  Serial.println("D = Drill & Fan (> 90)");
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
        if (i == 0)
        {
          if (!isDigit(inString[i]) && inString[i] != '-')
          {
            num = false;
            break;
          }
        }
        else if (!isDigit(inString[i]))
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

        if (both)
        {
          s1.write(temp);
          s2.write(temp);
        }
        else if (!actuator)
        {
          currentServo->write(temp);
        }
        else if (temp < 0) {
          analogWrite(PIN_ACTUATOR_DOWN, abs(temp));
          analogWrite(PIN_ACTUATOR_UP, 0);
        }
        else {
          analogWrite(PIN_ACTUATOR_UP, temp);
          analogWrite(PIN_ACTUATOR_DOWN, 0);
        }
      }
      else
      {
        if (inString == "A" || inString == "a")
        {
          both = false;
          actuator = false;
          currentServo = &s1;
          Serial.println("Selected Drill");
        }
        else if (inString == "B" || inString == "b")
        {
          both = false;
          actuator = false;
          currentServo = &s2;
          Serial.println("Selected Fan");
        }
        else if (inString == "C" || inString == "c")
        {
          both = false;
          actuator = true;
          Serial.println("Selected Actuator");
        }
        else if (inString == "D" || inString == "d")
        {
          both = true;
          actuator = false;
          Serial.println("Selected Both");
        }
        else
        {
          Serial.println("Stopping all motors.");
          s1.write(90);
          s2.write(90);
          analogWrite(PIN_ACTUATOR_UP, 0);
          analogWrite(PIN_ACTUATOR_DOWN, 0);
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
}
