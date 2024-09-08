#include <ArduinoJson.h>

void setup() {
  Serial.begin(9600);

  // Create a JSON document
  StaticJsonDocument<300> doc;

  // Add basic key-value pairs
  doc["sensor"] = "DHT22";
  doc["temperature"] = 24.6;  // Random temperature value
  doc["humidity"] = 45.8;     // Random humidity value

  // Create an array and add it to the JSON object
  JsonArray dataArray = doc["data"].to<JsonArray>();
  dataArray.add(10);
  dataArray.add(20);
  dataArray.add(30);  // Random array values

  // Create a nested object
  JsonObject location = doc["location"].to<JsonObject>();
  location["latitude"] = 37.7749;  // Random latitude
  location["longitude"] = -122.4194;  // Random longitude

  // Serialize the JSON document to a string
  String output;
  serializeJson(doc, output);

  // Print the serialized JSON string
  Serial.println("Serialized JSON:");
  Serial.println(output);
}

void loop() {
  // Your code here
}
