/*
 * Smart Greenhouse - Arduino (Device Layer)
 * IAD591 Final Project
 *
 * Reads DHT22 (temp+humidity) + LDR (light), controls LED grow-light + Servo vent.
 * Talks to Raspberry Pi over USB cable (Serial / 9600). NO TX/RX jumper wires.
 *
 * Protocol:
 *   Arduino -> Pi : one JSON line per second:
 *     {"temp":27.5,"hum":60,"light":480,"led":1,"vent":0,"fire":0,"mode":"auto"}
 *   Pi -> Arduino : single-line text commands ending with newline:
 *     LED:1   LED:0          (grow light on/off)
 *     VENT:1  VENT:0         (servo open/close)
 *     MODE:AUTO  MODE:MANUAL (control mode)
 *     TH_TEMP:30             (auto temp threshold, C)
 *     TH_LIGHT:400           (auto light threshold, raw ADC)
 *     TH_FIRE:50             (fire/overheat temp threshold, C)
 *
 * LAYER 1 (safe core): DHT22 + LDR + LED  -> always works.
 * LAYER 2 (optional):  Servo + LCD        -> #define-guarded.
 * KILLER FEATURE: fire/overheat protection -> temp >= TH_FIRE triggers buzzer
 *                 alarm + auto-open vent + "fire" flag to Pi (dashboard red alert).
 *                 (The 4-digit display is driven by the Raspberry Pi, not here.)
 */

#include <DHT.h>

// ---- LAYER 2 toggles: comment a line out to disable that hardware ----
#define USE_SERVO
#define USE_LCD
// ----------------------------------------------------------------------

#ifdef USE_SERVO
  #include <Servo.h>
  Servo vent;
  const int SERVO_PIN = 9;     // PWM pin
#endif

#ifdef USE_LCD
  #include <Wire.h>
  #include <LiquidCrystal_I2C.h>
  LiquidCrystal_I2C lcd(0x27, 16, 2);   // try 0x3F if 0x27 shows nothing
  bool lcdOk = false;
#endif

// ---- pins ----
const int DHT_PIN  = 2;
const int LDR_PIN  = A0;       // LDR voltage divider middle -> A0
const int LED_PIN  = 7;        // single grow-light LED (+220ohm)
const int BUZZ_PIN = 8;        // ACTIVE buzzer for fire alarm (HIGH=beep). +->D8, ->GND

#define DHT_TYPE DHT22      // using DHT22 (AM2302) — more accurate than DHT11
DHT dht(DHT_PIN, DHT_TYPE);

// ---- state ----
bool   ledOn      = false;
bool   ventOpen   = false;
bool   autoMode   = true;
bool   fire       = false;     // fire/overheat alarm active
float  thTemp     = 30.0;      // open vent above this temp
int    thLight    = 400;       // turn LED on below this light (raw 0..1023)
float  thFire     = 50.0;      // fire/overheat alarm at/above this temp

float  temp = 0, hum = 0;
int    light = 0;

unsigned long lastReport = 0;
const unsigned long REPORT_MS = 1000;

void setVent(bool open) {
  ventOpen = open;
#ifdef USE_SERVO
  vent.write(open ? 90 : 0);   // 90deg = open, 0deg = closed
#endif
}

void setLed(bool on) {
  ledOn = on;
  digitalWrite(LED_PIN, on ? HIGH : LOW);
}

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZ_PIN, OUTPUT);
  digitalWrite(BUZZ_PIN, LOW);
  dht.begin();

#ifdef USE_SERVO
  vent.attach(SERVO_PIN);
  setVent(false);
#endif

#ifdef USE_LCD
  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Smart Greenhouse");
  lcdOk = true;
#endif

  setLed(false);
}

void readSensors() {
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  // DHT22 occasionally returns NaN; keep last good value (demo never shows junk)
  if (!isnan(t)) temp = t;
  if (!isnan(h)) hum  = h;
  light = analogRead(LDR_PIN);   // higher value depends on wiring; calibrate threshold
}

void applyAutoLogic() {
  if (!autoMode) return;
  // Grow light: turn on when it's dark (light reading below threshold)
  setLed(light < thLight);
#ifdef USE_SERVO
  // Vent: open when too hot
  setVent(temp > thTemp);
#endif
}

// Fire/overheat protection — ALWAYS active (safety overrides mode).
// temp >= thFire  -> raise alarm: buzzer + force vent open (smoke/heat escape).
void checkFire() {
  fire = (temp >= thFire);
  if (fire) {
#ifdef USE_SERVO
    setVent(true);              // safety: open vent regardless of mode
#endif
  }
}

// Buzzer pattern: loud intermittent beep while fire active (called every loop).
void updateBuzzer() {
  if (!fire) { digitalWrite(BUZZ_PIN, LOW); return; }
  // beep ~3x/second
  digitalWrite(BUZZ_PIN, (millis() / 150) % 2 ? HIGH : LOW);
}

void updateLcd() {
#ifdef USE_LCD
  if (!lcdOk) return;
  if (fire) {                         // fire takes over the whole screen
    lcd.setCursor(0, 0);
    lcd.print("!! FIRE  ALARM !!");
    lcd.setCursor(0, 1);
    lcd.print("T:");
    lcd.print(temp, 1);
    lcd.print((char)223);
    lcd.print("C VENT OPEN ");
    return;
  }
  lcd.setCursor(0, 0);
  lcd.print("T:");
  lcd.print(temp, 1);
  lcd.print((char)223);            // degree symbol
  lcd.print("C H:");
  lcd.print((int)hum);
  lcd.print("% ");
  lcd.setCursor(0, 1);
  lcd.print(autoMode ? "AUTO " : "MAN  ");
  lcd.print("L:");
  lcd.print(ledOn ? "ON " : "OFF");
  lcd.print(ventOpen ? " V:O" : " V:C");
#endif
}

void report() {
  // JSON one-liner -> Pi
  Serial.print("{\"temp\":");  Serial.print(temp, 1);
  Serial.print(",\"hum\":");   Serial.print(hum, 1);
  Serial.print(",\"light\":"); Serial.print(light);
  Serial.print(",\"led\":");   Serial.print(ledOn ? 1 : 0);
  Serial.print(",\"vent\":");  Serial.print(ventOpen ? 1 : 0);
  Serial.print(",\"fire\":");  Serial.print(fire ? 1 : 0);
  Serial.print(",\"mode\":\"");Serial.print(autoMode ? "auto" : "manual");
  Serial.println("\"}");
}

void handleCommand(String c) {
  c.trim();
  if (c.length() == 0) return;

  if      (c == "LED:1")        { autoMode = false; setLed(true);  }
  else if (c == "LED:0")        { autoMode = false; setLed(false); }
  else if (c == "VENT:1")       { autoMode = false; setVent(true); }
  else if (c == "VENT:0")       { autoMode = false; setVent(false);}
  else if (c == "MODE:AUTO")    { autoMode = true;  }
  else if (c == "MODE:MANUAL")  { autoMode = false; }
  else if (c.startsWith("TH_TEMP:"))  { thTemp  = c.substring(8).toFloat(); }
  else if (c.startsWith("TH_LIGHT:")) { thLight = c.substring(9).toInt();   }
  else if (c.startsWith("TH_FIRE:"))  { thFire  = c.substring(8).toFloat(); }
}

void loop() {
  // read incoming command lines without blocking
  while (Serial.available()) {
    String c = Serial.readStringUntil('\n');
    handleCommand(c);
  }

  // buzzer must update every loop (not just once per second) for a crisp beep
  updateBuzzer();

  unsigned long now = millis();
  if (now - lastReport >= REPORT_MS) {
    lastReport = now;
    readSensors();
    checkFire();        // safety check runs every cycle, overrides mode
    applyAutoLogic();
    updateLcd();
    report();
  }
}
