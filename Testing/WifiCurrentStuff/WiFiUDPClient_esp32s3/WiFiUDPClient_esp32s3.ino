/*
 *  This sketch sends random data over UDP on a ESP32 device
 *
 */
#include <WiFi.h>
#include <WiFiUdp.h>

// WiFi network name and password:
//const char * networkName = "SETUP-FF56"; 
//const char * networkPswd = "chart4903cattle";

const char * networkName = "BOOMERSOONER"; 
const char * networkPswd = "NasaBound";
int CURRENT_SENSOR_PIN = A10;

//IP address to send UDP data to:
// either use the ip address of the server or 
// a network broadcast address
//const char * udpAddress = "192.168.0.88"; // ip of receiver
const char * udpAddress = "192.168.1.6";
const int udpPort = 3333; // unused port on receiver computer

//Are we currently connected?
boolean connected = false;

float average_current = 0.0;
int count = 0;

//The udp library class
WiFiUDP udp;

void setup(){
  // Initilize hardware serial:
  Serial.begin(115200);
  
  //Connect to the WiFi network
  connectToWiFi(networkName, networkPswd);
}

void loop(){
  // increment count cycling 0-9
  count = (count+1) % 10;
  
  // read current sensor
  float sensor_voltage = analogRead(CURRENT_SENSOR_PIN);
  sensor_voltage = (sensor_voltage / 4096) * 3.3*2;
  // read sensor and convert to amps (assumes 3.34volt Vref and 4096 ADC precision)
  float current_reading = ((sensor_voltage - 2.35) / 0.066);
  average_current = average_current + current_reading;
  
  if (count == 9) {
    average_current = average_current / 10.0;
      //only send data when connected
    if(connected){
      //Send a packet
      udp.beginPacket(udpAddress,udpPort);
      udp.printf("%.3f", average_current);
      Serial.print("Current Reading: ");
      Serial.print(average_current, 3);  // 3 specifies the number of decimal places to print
      Serial.print(" Sensor Voltage: ");
      Serial.println(sensor_voltage, 3);
      udp.endPacket();
    }
    average_current = 0;
  }
  

  //Wait for 1 second
  delay(100);
}

void connectToWiFi(const char * ssid, const char * pwd){
  Serial.println("Connecting to WiFi network: " + String(ssid));

  // delete old config
  WiFi.disconnect(true);
  //register event handler
  WiFi.onEvent(WiFiEvent);
  
  //Initiate connection
  WiFi.begin(ssid, pwd);

  Serial.println("Waiting for WIFI connection...");
}

//wifi event handler
void WiFiEvent(WiFiEvent_t event){
    switch(event) {
      case ARDUINO_EVENT_WIFI_STA_GOT_IP:
          //When connected set 
          Serial.print("WiFi connected! IP address: ");
          Serial.println(WiFi.localIP());  
          //initializes the UDP state
          //This initializes the transfer buffer
          udp.begin(WiFi.localIP(),udpPort);
          connected = true;
          break;
      case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
          Serial.println("WiFi lost connection");
          connected = false;
          break;
      default: break;
    }
}
