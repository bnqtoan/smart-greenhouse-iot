"""
4-digit 7-segment display driver — runs on the RASPBERRY PI (GPIO), via 74HC595.

This satisfies the rubric "LED 4 digit" in the Raspberry Pi row: the Pi itself
drives the display. The Arduino sends sensor data over USB; the Pi decides what
to show and pushes it to the 4-digit display.

Hardware (separate breadboard, powered from Pi 3.3V — no level shifter):
  74HC595   ->  Pi (BCM numbering)
  ----------------------------------
  DS   (14, data)   -> GPIO17
  STCP (12, latch)  -> GPIO27
  SHCP (11, clock)  -> GPIO22
  VCC  (16)         -> 3.3V       MR(10)->3.3V   OE(13)->GND
  GND  (8)          -> GND
  Q0..Q7 -> segments a,b,c,d,e,f,g,dp (via 220-330Ω)
  4 digit-common pins -> GPIO23,24,25,12 (common-cathode: LOW = digit on)

Display: shows temperature (e.g. "27.5") normally; shows "FirE" when fire alarm.
Multiplexes the 4 digits fast so all appear lit.

Graceful: if RPi.GPIO is unavailable (e.g. running on a laptop, or display not
wired) this module does nothing — the rest of the app runs normally.
"""
import time
import threading

# BCM pins
DS, STCP, SHCP = 17, 27, 22          # 74HC595 data, latch, clock
DIGITS = [23, 24, 25, 12]            # common pins for digit 1..4 (LOW = on)

# segment bit map for 74HC595 outputs Q0..Q7 = a,b,c,d,e,f,g,dp
SEG = {
    '0': 0b00111111, '1': 0b00000110, '2': 0b01011011, '3': 0b01001111,
    '4': 0b01100110, '5': 0b01101101, '6': 0b01111101, '7': 0b00000111,
    '8': 0b01111111, '9': 0b01101111, '-': 0b01000000, ' ': 0b00000000,
    'F': 0b01110001, 'i': 0b00010000, 'r': 0b01010000, 'E': 0b01111001,
    'C': 0b00111001, 'H': 0b01110110, 'o': 0b01011100, 't': 0b01111000,
}
DP = 0b10000000  # decimal point bit

class SevenSeg:
    def __init__(self):
        self.ok = False
        self.text = "    "      # 4 chars to show
        self.dp_pos = -1        # which digit has the decimal point (-1 none)
        self._stop = False
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            for p in (DS, STCP, SHCP, *DIGITS):
                GPIO.setup(p, GPIO.OUT)
                GPIO.output(p, GPIO.LOW)
            for d in DIGITS:
                GPIO.output(d, GPIO.HIGH)   # all digits off (common-cathode: HIGH=off)
            self.ok = True
        except Exception as e:
            print(f"[7seg] GPIO unavailable ({e}) -> 4-digit display disabled")

    def _shift(self, bits):
        G = self.GPIO
        G.output(STCP, G.LOW)
        for i in range(8):                  # MSB first
            G.output(SHCP, G.LOW)
            G.output(DS, G.HIGH if (bits & (0x80 >> i)) else G.LOW)
            G.output(SHCP, G.HIGH)
        G.output(STCP, G.HIGH)

    def set_value(self, text, dp_pos=-1):
        """text: up to 4 chars; dp_pos: index (0..3) of digit showing a dot."""
        self.text = (text + "    ")[:4]
        self.dp_pos = dp_pos

    def _render_once(self):
        G = self.GPIO
        for i, ch in enumerate(self.text):
            bits = SEG.get(ch, 0)
            if i == self.dp_pos:
                bits |= DP
            self._shift(bits)
            G.output(DIGITS[i], G.LOW)      # turn this digit on
            time.sleep(0.002)               # ~2ms per digit -> flicker-free
            G.output(DIGITS[i], G.HIGH)     # off before next

    def run(self):
        """Multiplex loop — call in a thread."""
        if not self.ok:
            return
        while not self._stop:
            self._render_once()

    def stop(self):
        self._stop = True
        if self.ok:
            try:
                for d in DIGITS:
                    self.GPIO.output(d, self.GPIO.HIGH)
                self.GPIO.cleanup()
            except Exception:
                pass


def format_temp(temp):
    """Return (text, dp_pos) for a temperature like 27.5 -> '27.5' with dot at idx1.
    Falls back to integer + 'C' if out of 0..99.9 range."""
    try:
        t = float(temp)
    except (TypeError, ValueError):
        return ("----", -1)
    if 0 <= t < 100:
        s = f"{t:04.1f}"            # e.g. '27.5' -> '27.5' (4 chars incl dot? no)
        # '27.5' has a dot; strip it and track position
        whole, frac = f"{t:.1f}".split(".")
        whole = whole.rjust(2)
        text = (whole + frac)[:3] + "C"   # e.g. '275C'
        return (text, 1)                   # dot after 2nd digit -> "27.5C" feel
    return (f"{int(t)}".rjust(3)[:3] + "C", -1)
