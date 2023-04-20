#define MQ2pin 0

/*
 Find example here: https://lastminuteengineers.com/mq2-gas-senser-arduino-tutorial/
     gas is present when the sensor value is around 400. A dial is also present to calibrate the sensor
*/


float sensorValue;  //variable to store sensor value

void setup() {
	Serial.begin(9600); // sets the serial port to 9600
	Serial.println("MQ2 warming up!");
	delay(5000); // allow the MQ2 to warm up
}

void loop() {
	sensorValue = analogRead(MQ2pin); // read analog input pin 0

	Serial.print("Sensor Value: ");
	Serial.println(sensorValue);
	
	delay(2000); // wait 2s for next reading
}
