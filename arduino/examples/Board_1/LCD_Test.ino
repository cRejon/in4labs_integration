/*
  Sketch name: LCD Test
  UNED Arduino IoT lab.

  Demonstrates the use a 16x2 LCD display.  The LiquidCrystal
  library works with all LCD displays that are compatible with the
  Hitachi HD44780 driver. 

  This sketch prints "Hello World!" to the LCD and shows the time in seconds 
  since the Arduino was reset.
  It also uses the display() and noDisplay() functions to turn on and off
  the display.

  The circuit:
    - LCD RS pin to digital pin 3
    - LCD Enable pin to digital pin 4
    - LCD D4 pin to digital pin 5
    - LCD D5 pin to digital pin 6
    - LCD D6 pin to digital pin 9
    - LCD D7 pin to digital pin 10
    - LCD R/W pin to ground
    - LCD VSS pin to ground
    - LCD VCC pin to 5V
    - LCD LED+ to 5V through a 220 ohm resistor
    - LCD LED- to ground
    - 10K potentiometer:
      - ends to +5V and ground
      - wiper to LCD VO pin 
*/

#include <LiquidCrystal.h> // include the library

// initialize the library by associating any needed LCD interface pin
// with the arduino pin number it is connected to
const int rs = 3, en = 4, d4 = 5, d5 = 6, d6 = 9, d7 = 10;;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

void setup() {
  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
  // Print a message to the LCD.
  lcd.print("Hello world!!");
}

void loop() {
  // set the cursor to column 0, line 1
  // (note: line 1 is the second row, since counting begins with 0):
  lcd.setCursor(0, 1);
  // print the number of seconds since reset:
  lcd.print(millis() / 1000);

  // turn off the display:
  lcd.noDisplay();
  delay(500);
  // turn on the display:
  lcd.display();
  delay(500);
}