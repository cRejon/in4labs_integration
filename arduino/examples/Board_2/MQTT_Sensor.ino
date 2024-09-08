#include <WiFi.h>
#include <PubSubClient.h>

// Network credentials
const char* ssid = "In4Labs-WiFi";
const char* password = "password";

// MQTT Broker
const char* mqtt_server = "192.168.4.1"; 
const char* client_id = "SensorBoardClient"; 
const char* output_topic = "output_topic"; 
const char* input_topic = "input_topic"; 

WiFiClient espClient;
PubSubClient client(espClient);

// This is the callback function that will be called when a message is received
void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  Serial.print("Message: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
  }
  Serial.println();
}

void setup() {
  // Start the Serial communication to display messages on the serial monitor
  Serial.begin(9600);

  // Connect to WiFi
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Connected to WiFi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Set the MQTT server and callback function
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  // Attempt to connect to the MQTT broker
  connectToMQTT();
}

void loop() {
  // Ensure the connection to the MQTT broker is maintained
  if (!client.connected()) {
    connectToMQTT();
  }
  client.loop();  // Keep the connection alive

  // Publish a message to the MQTT broker every 5 seconds
  static unsigned long lastMsgTime = 0;
  unsigned long now = millis();
  if (now - lastMsgTime > 5000) {
    lastMsgTime = now;
    publishMessage("Hello from Arduino Nano ESP32!");
  }
}

void connectToMQTT() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    // Attempt to connect to the MQTT broker with a client ID
    if (client.connect(client_id)) {
      Serial.println("connected");
      
      // Subscribe to a topic
      client.subscribe(input_topic);
      Serial.println("Subscribed to topic: your_topic");

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" trying again in 5 seconds");

      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void publishMessage(const char* message) {
  Serial.print("Publishing message: ");
  Serial.println(message);
  
  // Publish the message to the specified topic
  client.publish(output_topic, message);
}
