#include <EtherCard.h>
#include <IPAddress.h>
#include <Servo.h>

// Set equal to 1 for serial debugging
#define DEBUG_MODE 0

// Note: analogWrite() can not be used on pins 9 or 10 because of the servo library.
// Servos can still be used on those pins though

// The ethernet adapter uses pins 10, 11, 12, and 13

// 3, 5, 6
#define BASE_PIN A0
#define SHOULDER_PIN A4
#define ELBOW_PIN A3
#define CLAW_OPEN 8
#define CLAW_CLOSE 9

#define WRIST_L1_PIN 2
#define WRIST_L2_PIN 3
#define WRIST_L_SPEED_PIN 4

#define WRIST_R1_PIN 7
#define WRIST_R2_PIN 6
#define WRIST_R_SPEED_PIN 5

#define DEVICE_ID 1

String inString = "";
bool both = false;
bool actuator = false;

//
unsigned char base_speed = 90;
unsigned char shoulder_pos = 135;
unsigned char elbow_pos = 119;
char wristTheta_speed = 0;
char wristPhi_speed = 0;
int claw_dir = 1;

bool stopped = false;

unsigned char serialHash = 0;
unsigned char myHash = 81;

unsigned long timeOut = 0;

// talon/servo
Servo base, shoulder, elbow;
Servo* current;
int option = 0;

int parse_character(char c) {
  switch (c)
  {
  case 'A':
    Serial.print("Base val: ");
    Serial.println(base_speed);
    return 0;
  case 'B':
    Serial.print("Shoulder val: ");
    Serial.println(shoulder_pos);
    return 1;
  case 'C':
    Serial.print("Elbow val: ");
    Serial.println(elbow_pos);
    return 2;
  case 'D':
    Serial.print("Wrist Theta: ");
    Serial.println((int)wristTheta_speed);
    return 3;
  case 'E':
    Serial.print("Wrist Phi: ");
    Serial.println((int)wristPhi_speed);
    return 4;
  case 'F':
    Serial.print("Claw dir: ");
    Serial.println(claw_dir);
    return 5;
  case 'S':
    return 10;
  default:
    return -1;
  }
}


void updateServos()
{
  base.write(base_speed);
  shoulder.write(shoulder_pos);
  elbow.write(elbow_pos);
#if DEBUG_MODE
//  Serial.print("shoulder: ");
//  Serial.println(shoulder_pos);
//  Serial.print("elbow: ");
//  Serial.println(elbow_pos);
#endif
  if (claw_dir == 2) {
    digitalWrite(CLAW_OPEN, HIGH);
    digitalWrite(CLAW_CLOSE, LOW);
  } else if (claw_dir == 0) {
    digitalWrite(CLAW_OPEN, LOW);
    digitalWrite(CLAW_CLOSE, HIGH);
  } else {
    digitalWrite(CLAW_OPEN, LOW);
    digitalWrite(CLAW_CLOSE, LOW);
  }
  wristPhi_speed = int(wristPhi_speed);
  wristTheta_speed = int(wristTheta_speed);

  int offset = 0;
  // Right now we can't rotate and tilt ar the same time we'll need to fix this later
  if (wristTheta_speed > 0)
  {
    digitalWrite(WRIST_L1_PIN, HIGH);
    digitalWrite(WRIST_L2_PIN, LOW);
    analogWrite(WRIST_L_SPEED_PIN, abs(wristTheta_speed + offset) * 2);
    digitalWrite(WRIST_R1_PIN, HIGH);
    digitalWrite(WRIST_R2_PIN, LOW);
    analogWrite(WRIST_R_SPEED_PIN, abs(wristTheta_speed + offset) * 2);
    Serial.print("wrist go up: ");
    Serial.println(abs(wristTheta_speed + offset) *2);
    
    return;
  }
  if (wristTheta_speed < 0)
  {
    digitalWrite(WRIST_L1_PIN, LOW);
    digitalWrite(WRIST_L2_PIN, HIGH);
    analogWrite(WRIST_L_SPEED_PIN, abs(wristTheta_speed + offset) * 2);
    digitalWrite(WRIST_R1_PIN, LOW);
    digitalWrite(WRIST_R2_PIN, HIGH);
    analogWrite(WRIST_R_SPEED_PIN, abs(wristTheta_speed + offset) * 2);
    Serial.println("wrist go down");
    return;
  }
  if (wristPhi_speed > 0)
  {
    digitalWrite(WRIST_L1_PIN, HIGH);
    digitalWrite(WRIST_L2_PIN, LOW);
    analogWrite(WRIST_L_SPEED_PIN, abs(wristPhi_speed + offset) * 2);
    digitalWrite(WRIST_R1_PIN, LOW);
    digitalWrite(WRIST_R2_PIN, HIGH);
    analogWrite(WRIST_R_SPEED_PIN, abs(wristPhi_speed + offset) * 2);
    Serial.println("wrist rolls right"); 

    return;
  }
  if (wristPhi_speed < 0)
  {
    digitalWrite(WRIST_L1_PIN, LOW);
    digitalWrite(WRIST_L2_PIN, HIGH);
    analogWrite(WRIST_L_SPEED_PIN, abs(wristPhi_speed + offset) * 2);
    digitalWrite(WRIST_R1_PIN, HIGH);
    digitalWrite(WRIST_R2_PIN, LOW);
    analogWrite(WRIST_R_SPEED_PIN, abs(wristPhi_speed + offset) * 2);
    Serial.println("wrist roll left");
    return;
  }
  if (wristPhi_speed == 0 && wristTheta_speed == 0)
  {
    digitalWrite(WRIST_L1_PIN, LOW);
    digitalWrite(WRIST_L2_PIN, LOW);
    analogWrite(WRIST_L_SPEED_PIN, 0);
    digitalWrite(WRIST_R1_PIN, LOW);
    digitalWrite(WRIST_R2_PIN, LOW);
    analogWrite(WRIST_R_SPEED_PIN, 0);
  }
}

void setup()
{
  Serial.begin(9600);
  Serial.println("Enter a number to set a speed:");
  Serial.println("90 is still (if motor controllers are calibrated).");
  Serial.println("Talon motor controllers should be calibrated to range of 10-170.");
  Serial.println();
  Serial.println("Enter a character to select motors:");
  Serial.println("A = Base");
  Serial.println("B = Shoulder");
  Serial.println("C = Elbow");
//  Serial.println("D = 
  Serial.println("D = Wrist Up/Down");
  Serial.println("E = Wrist Left/Right");
  Serial.println("F = Claw");

  // servo/talon pins
  base.attach(BASE_PIN);
  shoulder.attach(SHOULDER_PIN);
  elbow.attach(ELBOW_PIN);

  base.write(base_speed);
  shoulder.write(shoulder_pos);
  elbow.write(elbow_pos);
  

  // wrist motor pins
  pinMode(WRIST_L1_PIN, OUTPUT);
  pinMode(WRIST_L2_PIN, OUTPUT);
  pinMode(WRIST_L_SPEED_PIN, OUTPUT);
  pinMode(WRIST_R1_PIN, OUTPUT);
  pinMode(WRIST_R2_PIN, OUTPUT);
  pinMode(WRIST_R_SPEED_PIN, OUTPUT);
  pinMode(CLAW_OPEN, OUTPUT);
  pinMode(CLAW_CLOSE, OUTPUT);

  digitalWrite(WRIST_L1_PIN, LOW);
  digitalWrite(WRIST_L2_PIN, LOW);
  analogWrite(WRIST_L_SPEED_PIN, 0);
  digitalWrite(WRIST_R1_PIN, LOW);
  digitalWrite(WRIST_R2_PIN, LOW);
  analogWrite(WRIST_R_SPEED_PIN, 0);
  digitalWrite(CLAW_OPEN, LOW);
  digitalWrite(CLAW_CLOSE, LOW);
}

void loop()
{
  while (Serial.available())
  {
    inString = Serial.readStringUntil('\n');
    if (inString.length() > 0) {
      char start = inString[0];
      int selection = parse_character(start);
      if (selection == -1) {
        int speed = inString.toInt();
        switch (option)
        {
        case 0:
          base_speed = speed;
          Serial.print("Base set to ");
          Serial.println(speed);
          break;
        case 1:
          shoulder_pos = speed;
          Serial.print("Shoulder set to ");
          Serial.println(speed);
          break;
        case 2:
          elbow_pos = speed;
          Serial.print("Elbow set to ");
          Serial.println(speed);
          break;
        case 3:
          wristTheta_speed = speed - 90;
          Serial.print("wrist theta set to ");
          Serial.println(wristTheta_speed);
          break;
        case 4:
          wristPhi_speed = speed - 90;
          Serial.print("wrist phi set to ");
          Serial.println(wristPhi_speed);
          break;
        case 5:
          if (speed < 90)
          {
            Serial.println("claw closing");
            claw_dir = 0;
          } else if (speed == 90)
          {
            Serial.println("claw stopped");
            claw_dir = 1;
          } else {
            Serial.println("claw opening");
            claw_dir = 2;
          }
        default:
          break;
        }
      } else if (selection == 10) {
          Serial.println("Reset all motors");
          base_speed = 90;
          shoulder_pos = 135;
          elbow_pos = 119;
          wristTheta_speed = 0;
          wristPhi_speed = 0;
          claw_dir = 1;
      }
      else {
        option = selection;
      }
      updateServos();
    }

  //   if (inChar == '\n')
  //   {
  //     // check for number
  //     bool num = true;
  //     if (inString.length() == 0)
  //       num = false;
  //     for (int i = 0; i < inString.length(); i++)
  //     {
  //       if (i == 0)
  //       {
  //         if (!isDigit(inString[i]) && inString[i] != '-')
  //         {
  //           num = false;
  //           break;
  //         }
  //       }
  //       else if (!isDigit(inString[i]))
  //       {
  //         num = false;
  //         break;
  //       }
  //     }
  //     if (num)
  //     {
  //       // if a number, set the speed
  //       int temp = inString.toInt();
  //       Serial.println(temp);

  //       if (both)
  //       {
  //         talonFan.write(temp);
  //         talonDrill.write(temp);
  //       }
  //       else if (!actuator)
  //       {
  //         currentServo->write(temp);
  //       }
  //       else if (temp < 0) {
  //         analogWrite(PIN_ACTUATOR_DOWN, abs(temp));
  //         analogWrite(PIN_ACTUATOR_UP, 0);
  //       }
  //       else {
  //         analogWrite(PIN_ACTUATOR_UP, temp);
  //         analogWrite(PIN_ACTUATOR_DOWN, 0);
  //       }
  //     }
  //     else
  //     {
  //       if (inString == "A" || inString == "a")
  //       {
  //         both = false;
  //         actuator = false;
  //         currentServo = &talonDrill;
  //         Serial.println("Selected Drill");
  //       }
  //       else if (inString == "B" || inString == "b")
  //       {
  //         both = false;
  //         actuator = false;
  //         currentServo = &talonFan;
  //         Serial.println("Selected Fan");
  //       }
  //       else if (inString == "C" || inString == "c")
  //       {
  //         both = false;
  //         actuator = true;
  //         Serial.println("Selected Actuator");
  //       }
  //       else if (inString == "D" || inString == "d")
  //       {
  //         both = true;
  //         actuator = false;
  //         Serial.println("Selected Both");
  //       }
  //       else
  //       {
  //         Serial.println("Stopping all motors.");
  //         s1.write(90);
  //         s2.write(90);
  //         analogWrite(PIN_ACTUATOR_UP, 0);
  //         analogWrite(PIN_ACTUATOR_DOWN, 0);
  //       }
  //     }

  //     inString = "";
  //   }
  //   else
  //   {
  //     // add character to string
  //     inString += (char)inChar;
  //   }
  // }
  }
}
