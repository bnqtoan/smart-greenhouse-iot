/*
 * Smart Greenhouse — Wokwi simulation sketch
 *
 * This is a TRIMMED copy of arduino/greenhouse/greenhouse.ino made to run in
 * the Wokwi online simulator (https://wokwi.com) so the team can VERIFY the
 * wiring in diagram.json before touching real hardware.
 *
 * Open this folder at wokwi.com (or use the Wokwi VS Code extension) → it loads
 * diagram.json + this sketch and SIMULATES the circuit. Move the sliders on the
 * DHT22 / photoresistor to watch the LED + servo react.
 *
 * Pin map (identical to the real project):
 *   DHT22 DATA -> D2,  LDR AO -> A0,  LED+220R -> D7,  Servo -> D9,
 *   LCD1602 I2C -> A4/A5,  power 5V/GND via breadboard rails.
 *
 * For the REAL build, use arduino/greenhouse/greenhouse.ino (it adds USB-serial
 * JSON output to the Raspberry Pi). This sketch keeps only the local logic.
 */
#include <DHT.h>
#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define DHT_PIN 2
#define DHT_TYPE DHT22
#define LDR_PIN A0
#define LED_PIN 7
#define SERVO_PIN 9

DHT dht(DHT_PIN, DHT_TYPE);
Servo vent;
LiquidCrystal_I2C lcd(0x27, 16, 2);

float thTemp = 30.0;   // open vent above this
int   thLight = 400;   // LED on below this (raw ADC)

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  dht.begin();
  vent.attach(SERVO_PIN);
  vent.write(0);
  lcd.init();
  lcd.backlight();
  lcd.print("Smart Greenhouse");
}

void loop() {
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  int light = analogRead(LDR_PIN);
  if (isnan(t)) t = 0;
  if (isnan(h)) h = 0;

  bool ledOn = light < thLight;     // dark -> grow light on
  bool ventOpen = t > thTemp;       // hot  -> open vent
  digitalWrite(LED_PIN, ledOn ? HIGH : LOW);
  vent.write(ventOpen ? 90 : 0);

  lcd.setCursor(0, 0);
  lcd.print("T:"); lcd.print(t, 1); lcd.print((char)223); lcd.print("C H:"); lcd.print((int)h); lcd.print("% ");
  lcd.setCursor(0, 1);
  lcd.print("L:"); lcd.print(ledOn ? "ON " : "OFF"); lcd.print(ventOpen ? " V:O" : " V:C"); lcd.print("   ");

  Serial.print("{\"temp\":"); Serial.print(t,1);
  Serial.print(",\"hum\":");  Serial.print(h,1);
  Serial.print(",\"light\":");Serial.print(light);
  Serial.print(",\"led\":");  Serial.print(ledOn?1:0);
  Serial.print(",\"vent\":"); Serial.print(ventOpen?1:0);
  Serial.println("}");
  delay(1000);
}
