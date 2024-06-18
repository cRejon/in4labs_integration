/*
  Sketch name: Blink LED
  This example code is in the public domain. 
  Adapted for UNED Arduino IoT lab.

  Turns a LED on for a set delay time, then off, repeatedly.
  Default delay time is 1 second.
  
  Circuit:
    - RGB LED connected to pins A0 (red), A1 (green) and A2 (blue)

  Because this circuit uses a common catode RGB LED, the common leg is connected to the low voltage level
  and pins colors will be ON when they are set to HIGH voltage level, and OFF when they are set to LOW.
*/

// definitions:
#define RGB_PIN A0              // pin where the RGB LED is connected               
#define BLINK_DELAY 1000        // time in ms that the led is on/off

// the setup function runs once when the code is loaded
void setup() {
  pinMode(RGB_PIN, OUTPUT);     // initialize digital pin RGB_PIN as an output
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(RGB_PIN, HIGH);   // turn the LED on 
  delay(BLINK_DELAY);            // wait for set delay time 
  digitalWrite(RGB_PIN, LOW);    // turn the LED off 
  delay(BLINK_DELAY);            // wait for set delay time 
}