"""
4-digit 7-segment display driver — runs on the RASPBERRY PI (GPIO), via 74HC595.

Wiring follows the SunFounder Raphael-kit "1.1.5 4-Digit 7-Segment" reference
EXACTLY (the circuit the team is building). Do not change pins unless the
breadboard wiring changes.

  74HC595      -> Pi (BCM)
  -----------------------------
  DS   (data)  -> GPIO24    (SDI)
  STCP (latch) -> GPIO23    (RCLK)
  SHCP (clock) -> GPIO18    (SRCLK)
  VCC, MR      -> 3.3V      OE -> GND, GND -> GND
  Q0..Q7       -> segments a,b,c,d,e,f,g,dp (via 220-330Ω)
  4 digit commons -> GPIO 10, 22, 27, 17  (placePin, digit 0..3)

This display is COMMON-ANODE: segment codes are inverted (0=on), and a digit
is selected by driving its common pin HIGH (pickDigit). Matches SunFounder.

Shows temperature (e.g. "27.5") normally; "FirE" when fire alarm.
Graceful: if RPi.GPIO is unavailable, this module disables itself silently.
"""
import time

# --- SunFounder reference pins (BCM) — must match the wiring ---
SDI   = 24    # DS    (data)
RCLK  = 23    # ST_CP (latch)
SRCLK = 18    # SH_CP (clock)
placePin = (10, 22, 27, 17)   # digit 0,1,2,3 common pins (HIGH = on)

# Common-ANODE segment codes (bit=0 turns a segment ON). SunFounder 'number' table.
# bit order from 74HC595 Q7..Q0 = dp,g,f,e,d,c,b,a
DIGIT = {
    '0': 0xc0, '1': 0xf9, '2': 0xa4, '3': 0xb0, '4': 0x99,
    '5': 0x92, '6': 0x82, '7': 0xf8, '8': 0x80, '9': 0x90,
    ' ': 0xff, '-': 0xbf,
    # letters for "FirE" / status (segments a,b,c,d,e,f,g => inverted)
    'F': 0x8e, 'i': 0xfb, 'r': 0xaf, 'E': 0x86,
    'C': 0xc6, 'H': 0x89, 'o': 0xa3, 't': 0x87,
}
DP_MASK = 0x7f   # AND with this to turn the decimal point ON (clear dp bit)


class SevenSeg:
    def __init__(self):
        self.ok = False
        self.text = "    "
        self.dp_pos = -1
        self._stop = False
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(SDI, GPIO.OUT)
            GPIO.setup(RCLK, GPIO.OUT)
            GPIO.setup(SRCLK, GPIO.OUT)
            for p in placePin:
                GPIO.setup(p, GPIO.OUT)
            self.ok = True
        except Exception as e:
            print(f"[7seg] GPIO unavailable ({e}) -> 4-digit display disabled")

    def _shift(self, data):
        G = self.GPIO
        for i in range(8):
            G.output(SDI, 0x80 & (data << i))
            G.output(SRCLK, G.HIGH); G.output(SRCLK, G.LOW)
        G.output(RCLK, G.HIGH); G.output(RCLK, G.LOW)

    def _clear(self):
        self._shift(0xff)   # all segments off (common-anode: 1=off)

    def _pick(self, digit):
        G = self.GPIO
        for p in placePin:
            G.output(p, G.LOW)
        G.output(placePin[digit], G.HIGH)

    def set_value(self, text, dp_pos=-1):
        self.text = (text + "    ")[:4]
        self.dp_pos = dp_pos

    def run(self):
        """Multiplex the 4 digits continuously (call in a thread)."""
        if not self.ok:
            return
        while not self._stop:
            for i, ch in enumerate(self.text):
                code = DIGIT.get(ch, 0xff)
                if i == self.dp_pos:
                    code &= DP_MASK          # turn on decimal point
                self._clear()
                self._pick(i)
                self._shift(code)
                time.sleep(0.002)

    def stop(self):
        self._stop = True
        if self.ok:
            try:
                self.GPIO.cleanup()
            except Exception:
                pass


def format_temp(temp):
    """temp 27.5 -> ('27.5C'-ish 4 chars, dp index). Common display: '27.5'."""
    try:
        t = float(temp)
    except (TypeError, ValueError):
        return ("----", -1)
    if 0 <= t < 100:
        whole, frac = f"{t:.1f}".split(".")
        text = (whole.rjust(2) + frac)[:3] + "C"   # e.g. "275C"
        return (text, 1)                            # dot after 2nd digit => "27.5C"
    return (f"{int(t)}".rjust(3)[:3] + "C", -1)
