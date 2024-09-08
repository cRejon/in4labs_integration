#include <WiFi.h>  // Include the Wi-Fi library

// Network credentials
const char* ssid = "In4Labs-WiFi";
const char* password = "password";

void setup() {
  // Start the Serial communication to display messages on the serial monitor
  Serial.begin(9600);

  // Begin the WiFi connection process
  Serial.println("Connecting to WiFi...");

  // Connect to the specified WiFi network
  WiFi.begin(ssid, password);

  // Wait until the device is connected to the WiFi network
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  // Once connected, print the device's IP address
  Serial.println();
  Serial.println("Connected to WiFi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Your code here
}
