#include <Servo.h>

// Science package tester
// Currently can control the drill and fan

// Arduino Nano pins to attach Talon controllers to
#define PIN_S_1 6
#define PIN_S_2 7

// servo objects
Servo s1;
Servo s2;

// test program vars
String inString = "";
Servo* currentServo = &s1;
bool both = false;

void setup() {
  // setup servos
  s1.attach(PIN_S_1);
  s2.attach(PIN_S_2);
  
  s2.write(90);
  s1.write(90);
  
  // setup serial
  Serial.begin(9600);

  Serial.println("Enter a number to set a speed:");
  Serial.println("90 is still (if motor controllers are calibrated).");
  Serial.println("Talon motor controllers should be calibrated to range of 10-170.");
  Serial.println();
  Serial.println("Enter a character to select motors:");
  Serial.println("A = Drill (> 90)");
  Serial.println("B = Fan (> 90)");
  Serial.println("C = Drill & Fan (> 90)");
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
        else
        {
          currentServo->write(temp);
        }
      }
      else
      {
        if (inString == "A" || inString == "a")
        {
          both = false;
          currentServo = &s1;
          Serial.println("Selected Drill");
        }
        else if (inString == "B" || inString == "b")
        {
          both = false;
          currentServo = &s2;
          Serial.println("Selected Fan");
        }
        else if (inString == "C" || inString == "c")
        {
          both = true;
          Serial.println("Selected Both");
        }
        else
        {
          Serial.println("Stopping all motors.");
          s1.write(90);
          s2.write(90);
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
