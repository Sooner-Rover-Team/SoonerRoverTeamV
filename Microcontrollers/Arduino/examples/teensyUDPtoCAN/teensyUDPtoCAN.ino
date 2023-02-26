#include <Ethernet.h>
#include <EthernetUdp.h>
#include <FlexCAN.h>

// Set the MAC address and IP address of the Teensy
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(0, 0, 0, 0);  // Set this to the IP address you want to use
unsigned int localPort = 8888;  // Set the port number you want to use for receiving UDP packets

// Set up the CAN bus
FlexCAN can(1000000);  // Set the baud rate of the CAN bus

void setup() {
  // Initialize the Ethernet and CAN libraries
  Ethernet.begin(mac, ip);
  Udp.begin(localPort);
  can.begin();

  // Set the serial baud rate to 9600 for debugging
  Serial.begin(9600);
}

void loop() {
  // Check if there's a UDP packet available
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    // Read the UDP packet into a buffer
    byte buffer[8];
    Udp.read(buffer, packetSize);

    // Convert each byte in the buffer to a number
    int numbers[8];
    for (int i = 0; i < 8; i++) {
      numbers[i] = buffer[i];
    }

    // Send the numbers out through the CAN bus
    can.write(numbers, 8);

    // Print the received numbers to the serial monitor for debugging
    for (int i = 0; i < 8; i++) {
      Serial.print(numbers[i]);
      Serial.print(" ");
    }
    Serial.println();
  }
}
