#include <ACAN_T4.h>
#include <Servo.h>
#include <Adafruit_AHT10.h> // read temp/humidity sensor

/*
 * SCIENCE TEENSY:
 * - receives CAN msgs containing motor speeds
 * - writes out motor signals to motor controllers
 * - sends out CAN msgs containing sensor data (TODO)
 *
 * TALON for dril
 * H-Bridge for Big, small and test tube actuators
 * no motor controller for servo (its built in)
 */

// Set equal to 1 for serial debugging
#define DEBUG 1
// Message ID for science pckg
#define SCIENCE_ID 0x03

// ********** MOTOR PINS ***********
// Digital Outputs (H-bridge has 2 inputs)
#define BIG_ACT_UP_PIN 
#define BIG_ACT_DOWN_PIN

#define SMALL_ACT_UP_PIN
#define SMALL_ACT_DOWN_PIN

#define TEST_TUBE_UP_PIN
#define TEST_TUBE_DOWN_PIN
// PWM Outputs (TALON and Servo)
#define DRILL_PIN
#define SERVO_CAM_PIN

#define AHT10_A_PIN 24
#define AHT10_D_PIN 25
#define METHANE_PIN 14

// Object to read the sensor
Adafruit_AHT10 AHT10;

// servo objects for talon motor controllers
Servo drill;
// The current CAN message to be sent out
CANMessage message_received;
CANMessage message_sent;

// raw bytes to store from ethernet data
// they are converted to output ranges in updateServos()
uint8_t myHash = 0;
uint8_t serialHash = 0;
// used to store motor msg data
int bigActSpeed = 126;
int smallActSpeed = 126;
int testTubeSpeed = 126;
int drillSpeed = 90;
int servoCamPosition = 90;

// unsigned long msgTime
// stop motors if last msg recieved is more than 1 second
unsigned long stopTimeout = 0, turnTimeout = 0;

// callback that prints received packets to the serial port
void updateMotors(CANMessage message) {
  Serial.println("CAN MSG RECIEVED");

  // SCIENCE CAN msg (with msg.ID==0x03): [bigActuator, drill, smallActuator, testTubeActuator, servoCam]
  bigActSpeed = message.data[0];
  drillSpeed = message.data[1];
  smallActSpeed = message.data[2];
  testTubeSpeed = message.data[3];
  servoCamPosition = message.data[4];

  // // UDPATE BIG ACTUATOR
  // if (bigActSpeed > 126) {
  // digitalWrite(BIG_ACT_UP_PIN, HIGH);
  // digitalWrite(BIG_ACT_DOWN_PIN, LOW);
  // }
  // else if (bigActSpeed < 126) {
  // digitalWrite(BIG_ACT_UP_PIN, LOW);
  // digitalWrite(BIG_ACT_DOWN_PIN, HIGH);
  // }
  // else { // msg == 126 is neutral speed
  // digitalWrite(BIG_ACT_UP_PIN, LOW);
  // digitalWrite(BIG_ACT_DOWN_PIN, LOW);
  // }
  // // UDPATE SMALL ACTUATOR
  // if (smallActSpeed > 126) {
  // digitalWrite(SMALL_ACT_UP_PIN, HIGH);
  // digitalWrite(SMALL_ACT_DOWN_PIN, LOW);
  // }
  // else if (smallActSpeed < 126) {
  // digitalWrite(SMALL_ACT_UP_PIN, LOW);
  // digitalWrite(SMALL_ACT_DOWN_PIN, HIGH);
  // }
  // else { // msg == 126 is neutral speed
  // digitalWrite(SMALL_ACT_UP_PIN, LOW);
  // digitalWrite(SMALL_ACT_DOWN_PIN, LOW);
  // }
  // // UDPATE TEST TUBE ACTUATOR
  // if (testTubeSpeed > 126) {
  // digitalWrite(TEST_TUBE_UP_PIN, HIGH);
  // digitalWrite(TEST_TUBE_DOWN_PIN, LOW);
  // }
  // else if (testTubeSpeed < 126) {
  // digitalWrite(TEST_TUBE_UP_PIN, LOW);
  // digitalWrite(TEST_TUBE_DOWN_PIN, HIGH);
  // }
  // else { // msg == 126 is neutral speed
  // digitalWrite(TEST_TUBE_UP_PIN, LOW);
  // digitalWrite(TEST_TUBE_DOWN_PIN, LOW);
  // }
  // // UDPATE DRILL
  // drill.write(drillSpeed);
  // // UDPATE SERVO CAMERA POSITION
  // servoCam.write(servoCamPosition);
}

// Reads Sensor data and write out values to CAN
//  CAN MSG: [temperature, humidity, methane] msg.ID = 0x04?
void sendSensorData() {
  sensors_event_t humidity, temp;
  AHT10.getEvent(&humidity, &temp); // populate temp and humidity objects with fresh data
  byte data[4] = {0};
  // read temp/ humidity
  data[0] = temp.temperature;
  data[1] = humidity.relative_humidity;
  // read methane
  int sensor = analogRead(METHANE_PIN);
  Serial.println(sensor);
  data[2] = sensor / 256;
  data[3] = sensor % 256;

  #if DEBUG
    for(int i=0; i<4; i++) {
      Serial.print(uint64_t(data[i]));
      Serial.print(" ");
    }
    Serial.println();
  #endif
  
  // Ensure correct endianness if needed
  
  // Pack data into CAN message
  message_sent.id = 0x04; // low priority msg
  message_sent.len = 4; // 3 integers sent
  memcpy(message_sent.data, data, message_sent.len); // Copy sensor data into CAN msg

  // Try to send CAN message
  bool ok = ACAN_T4::can3.tryToSend(message_sent);
  if (ok && DEBUG) {
    // Serial.println("Sensor Data sent");
  }
}


void setup()
{
  // set up Serial Monitor
  #if DEBUG
    pinMode (LED_BUILTIN, OUTPUT) ;
    Serial.begin (115200) ;
    while (!Serial) {
      delay (50) ;
      digitalWrite (LED_BUILTIN, !digitalRead (LED_BUILTIN)) ;
    }
  #endif
  // set up CAN 
  ACAN_T4_Settings settings (100 * 1000) ; // 100 kbit/s - must agree on both ends of CAN
  const uint32_t errorCode = ACAN_T4::can3.begin (settings) ;
  if (0 == errorCode) {
    #if DEBUG
      Serial.println ("can3 ok") ;
    #endif
  }else{
    #if DEBUG
      Serial.print ("Error can3: 0x") ;
      Serial.println (errorCode, HEX) ;
    #endif
    while (1) {
      delay (100) ;
      #if DEBUG
        Serial.println ("Invalid setting") ;
      #endif
      digitalWrite (LED_BUILTIN, !digitalRead (LED_BUILTIN)) ;
    }
  }

  // setup temp / humidity sensor
  if (AHT10.begin()) {
    #if DEBUG
      Serial.println("Init AHT10 Success!");
    #endif
  } else {
    #if DEBUG
      Serial.println("INIT AHT10 Failed!");
    #endif
  }
  pinMode(METHANE_PIN, INPUT); // Set the D8 pin as a digital input pin

  // setup motor pins (3 actuators using digital signals)
  // pinMode(BIG_ACT_UP_PIN, OUTPUT);
  // pinMode(BIG_ACT_DOWN_PIN, OUTPUT);
  // pinMode(SMALL_ACT_UP_PIN, OUTPUT);
  // pinMode(SMALL_ACT_DOWN_PIN, OUTPUT);
  // pinMode(TEST_TUBE_UP_PIN, OUTPUT);
  // pindMode(TEST_TUBE_DOWN_PIN, OUTPUT);

  // // initialize pins to low (0v)
  // digitalWrite(BIG_ACT_UP_PIN, LOW);
  // digitalWrite(BIG_ACT_DOWN_PIN, LOW);
  // digitalWrite(SMALL_ACT_UP_PIN, LOW);
  // digitalWrite(SMALL_ACT_DOWN_PIN, LOW);
  // digitalWrite(TEST_TUBE_UP_PIN, LOW);
  // digitalWrite(TEST_TUBE_DOWN_PIN, LOW);

  // drill.attach(DRILL_PIN, 900, 2100);
  // servoCam.attach(servoCam, 900, 2100);
  // all motors should start in neutral position (resting for motors, 90 degrees for servos)
  // drill.write(90);
  // servoCam.write(90);

  // pinMode(CAROUSEL_LIMIT_PIN, INPUT_PULLUP); // digital signal
  // pinMode(MICROSCOPE_ENCODER_PIN, INPUT); // analog signal

}

void loop()
{
  // receive CAN message if one is available
  if (ACAN_T4::can3.receive (message_received)) {
    #if DEBUG // print the message for debugging
    Serial.println("Message received");
      if(message_received.id == 0x03) {
        Serial.print("ID=");
        Serial.print(message_received.id);
        Serial.print(" msg = ");
        for(int i=0; i<message_received.len; ++i) {
          Serial.print(message_received.data[i]);
          Serial.print(", ");
        }
        Serial.println();
      }
    #endif

    if(message_received.id == SCIENCE_ID) { // science id = 0x03
      if(message_received.len == 5) { // CAN performs it's own checksum so no need to check that
        updateMotors(message_received);
      }
    }
  } 
  // stopTimeout = millis();
  sendSensorData();
  
  // If switch is triggered while carousel is moving, stop carousel. This should allign test tube properly
//  if(!digitalRead(CAROUSEL_LIMIT_PIN) && carouselMoving && (carouselSpeed == 1)) {
//    //Serial.println("limited");
//    carousel.write(90);
//    carouselMoving = false;
//  }

  unsigned long curr_time = millis();
  // stop all motors after 1 second of no messages
  if (curr_time - stopTimeout >= 1000) {
    stopTimeout = millis();
    // drill.write(90);
    // servoCam.write(90);

    // digitalWrite(BIG_ACT_UP_PIN, LOW);
    // digitalWrite(BIG_ACT_DOWN_PIN, LOW);
    // digitalWrite(SMALL_ACT_UP_PIN, LOW);
    // digitalWrite(SMALL_ACT_DOWN_PIN, LOW);
    // digitalWrite(TEST_TUBE_UP_PIN, LOW);
    // digitalWrite(TEST_TUBE_DOWN_PIN, LOW);

    #if DEBUG
      Serial.println("Stopped motors");
    #endif
  }
}
