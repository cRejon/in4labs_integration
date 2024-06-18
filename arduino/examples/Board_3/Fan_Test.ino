/*
  Sketch name: Fan Test
  UNED Arduino IoT lab. 

  Use a relay to turns a 12V fan on and off repeatedly for a set delay time.
  Set time by default is 5 seconds.
  
  Circuit:
    - Fan (+) conected to 12 V (+)
    - Fan (-) conected to Relay NC (Normally Closed) 
    - Relay COM (common) to ground
    - Pin 2 connected to Relay Signal pin
     
  When pin 2 is set to LOW voltage the relay will open and the fan will turn OFF.
  When pin 2 is set to HIGH voltage the relay will close and the fan will turn ON.

*/

#define FAN_PIN 2        // connected to relay signal pin
#define BLINK_DELAY 5000  // time in ms that the fan is on/off

// the setup function runs once when the code is loaded
void setup() {
  pinMode(FAN_PIN, OUTPUT);     // initialize digital pin FAN_PIN as an output.
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(FAN_PIN, LOW);     // turn the fan off
  delay(BLINK_DELAY);              // wait for a second
  digitalWrite(FAN_PIN, HIGH);      // turn the fan on
  delay(BLINK_DELAY);              // wait for a second
}
