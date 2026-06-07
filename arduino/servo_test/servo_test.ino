/*
 * Standalone servo bit-bang test — flash this ALONE to verify the servo moves.
 * Nothing else (no DHT, no Bluetooth). If the servo sweeps open<->closed every
 * 2 seconds, bit-bang works and the values are right for your servo.
 *
 * Wiring: servo signal -> D9, servo + -> 5V, servo - -> GND.
 *
 * If it does NOT move:
 *   - try wider pulses: change CLOSED to 600 and OPEN to 2400
 *   - check servo power (5V + GND) and the signal wire on D9
 */
const int SERVO_PIN = 9;
int CLOSED = 1000;   // us (~0 deg)
int OPEN   = 2000;   // us (~90 deg)

void moveTo(int us) {
  for (int i = 0; i < 50; i++) {       // ~1 second of pulses
    digitalWrite(SERVO_PIN, HIGH);
    delayMicroseconds(us);
    digitalWrite(SERVO_PIN, LOW);
    delay(20);
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(SERVO_PIN, OUTPUT);
  digitalWrite(SERVO_PIN, LOW);
  Serial.println("Servo test start");
}

void loop() {
  Serial.println("OPEN");
  moveTo(OPEN);
  delay(1000);
  Serial.println("CLOSED");
  moveTo(CLOSED);
  delay(1000);
}
