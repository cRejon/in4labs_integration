/*
  Sketch name: DHT22 Sensor Test
  Code is based off the example code in the DHT library.
  Adapted for UNED Arduino IoT lab.

  Basic code that demonstrates the usage of the DHT sensor library,
  readings will be printed to the serial monitor every 2 seconds.

  Circuit:
    - DATA_PIN (pin 2) connected to sensor data line.
    - RGB LED connected to pins 5 (red), 6 (green) and 9 (blue)

  Humidity is read as relative humidiy 5% - 99%
  Temperature is read in Celsius (or Fahrenheit if selected) -40ºC to 80ºC
  Sensor values can be read into float or String variables.
*/

#include <DHT.h>                     // include the DHT library.

#define DATA_PIN 2                   // define the type data pin
#define DHT_TYPE DHT22               // define the DHT sensor (DHT11, DHT21, or DHT22)

DHT dht = DHT(DATA_PIN, DHT_TYPE);   // instantiate the dht class with our data pin and DHT type.

void setup() {
  Serial.begin(9600);             // initialize serial communication at 9600 bits per second
  dht.begin();                    // call the begin class in the dht object
}

void loop() {  
  float hum = dht.readHumidity();      // read the humidity from the sensor
  float temp = dht.readTemperature();  // read temperature as Celsius (the default), insert true as a parameter for fahrenheit
  
  Serial.print("Humidity: ");     // print the humidity value to serial
  Serial.print(hum);
  Serial.print(" %\t");
  Serial.print("Temperature: ");  // print the temperature value to serial
  Serial.print(temp);
  Serial.println(" C ");
  
  delay(2000);                    // wait 2 seconds before reading again  
}