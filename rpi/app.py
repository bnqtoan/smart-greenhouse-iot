"""
Smart Greenhouse - Raspberry Pi (Gateway + Application Layer)
IAD591 Final Project

Reads JSON lines from Arduino over USB (/dev/ttyACM0), stores in SQLite,
serves a Flask dashboard, and sends control commands back to Arduino.

Reliability design (lab hardware is flaky):
  - Serial runs in a background thread; main web app never blocks on it.
  - If the Arduino is not connected, the dashboard shows a "Chưa kết nối
    Arduino" status (no fake data); it auto-connects when the Arduino appears.
  - All DB writes are wrapped; a bad reading never crashes the server.

Run:  python3 app.py     then open http://<pi-ip>:5000
"""
import json
import sqlite3
import threading
import time
import os
from datetime import datetime
from flask import Flask, jsonify, request, render_template

# ---------------- config ----------------
# Try Bluetooth (HC-05 via rfcomm) FIRST, then fall back to USB. First that
# opens wins. This gives "Bluetooth with USB backup" automatically.
SERIAL_PORTS = ["/dev/rfcomm0", "/dev/ttyACM0", "/dev/ttyUSB0"]
BAUD_RATE    = 9600
DB_PATH     = os.path.join(os.path.dirname(__file__), "greenhouse.db")
APP_PORT    = 5000

# ---------------- shared state ----------------
state = {
    "temp": 0.0, "hum": 0.0, "light": 0,
    "led": 0, "vent": 0, "fire": 0, "mode": "auto",
    "source": "disconnected",  # "live" | "disconnected"
    "link": "",                # "bluetooth" | "usb"
    "updated": None,
}
state_lock = threading.Lock()

# pending command to push to Arduino (set by web, consumed by serial thread)
pending_cmd = []
cmd_lock = threading.Lock()

# ---------------- database ----------------
def db_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = db_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            temp REAL, hum REAL, light INTEGER,
            led INTEGER, vent INTEGER, mode TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_reading(d):
    try:
        conn = db_conn()
        conn.execute(
            "INSERT INTO readings (ts,temp,hum,light,led,vent,mode) VALUES (?,?,?,?,?,?,?)",
            (datetime.now().isoformat(timespec="seconds"),
             d["temp"], d["hum"], d["light"], d["led"], d["vent"], d["mode"])
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB write skipped:", e)

# ---------------- serial reader thread ----------------
def queue_cmd(cmd):
    with cmd_lock:
        pending_cmd.append(cmd)

def drain_cmds(ser):
    with cmd_lock:
        cmds = pending_cmd[:]
        pending_cmd.clear()
    for c in cmds:
        try:
            ser.write((c + "\n").encode())
        except Exception as e:
            print("serial write failed:", e)

def update_state(d, source):
    with state_lock:
        state.update(d)
        state["source"] = source
        state["updated"] = datetime.now().isoformat(timespec="seconds")

def open_first_port():
    """Open the first available port from SERIAL_PORTS (Bluetooth first, USB backup)."""
    import serial
    for port in SERIAL_PORTS:
        try:
            ser = serial.Serial(port, BAUD_RATE, timeout=1)
            print(f"[serial] connected {port}")
            return ser, port
        except Exception:
            continue
    raise IOError("no serial port available (tried " + ", ".join(SERIAL_PORTS) + ")")

def serial_loop():
    """Read JSON from Arduino over Bluetooth (rfcomm) or USB. Auto-reconnect."""
    last_save = 0
    while True:
        ser = None
        try:
            ser, port = open_first_port()
            time.sleep(2)  # let Arduino settle
            while True:
                drain_cmds(ser)
                line = ser.readline().decode(errors="ignore").strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue  # ignore boot text / partial lines
                clean = {
                    "temp": float(d.get("temp", 0)),
                    "hum": float(d.get("hum", 0)),
                    "light": int(d.get("light", 0)),
                    "led": int(d.get("led", 0)),
                    "vent": int(d.get("vent", 0)),
                    "fire": int(d.get("fire", 0)),
                    "mode": d.get("mode", "auto"),
                }
                # label transport: bluetooth (rfcomm) vs usb
                clean["link"] = "bluetooth" if "rfcomm" in port else "usb"
                update_state(clean, "live")
                now = time.time()
                if now - last_save >= 2:   # log every 2s
                    save_reading(clean)
                    last_save = now
        except Exception as e:
            print(f"[serial] not available ({e}) -> waiting for Arduino")
            if ser:
                try: ser.close()
                except: pass
            with state_lock:
                state["source"] = "disconnected"
                state["updated"] = datetime.now().isoformat(timespec="seconds")
        time.sleep(3)  # then retry real serial

# ---------------- 4-digit 7-seg (Pi GPIO via 74HC595) ----------------
def sevenseg_loop():
    """Push current temp (or 'FirE' on alarm) to the Pi-driven 4-digit display.
    Runs the multiplex render in its own thread; updates the value 5x/sec."""
    try:
        from sevenseg import SevenSeg, format_temp
    except Exception as e:
        print(f"[7seg] module unavailable ({e})")
        return
    disp = SevenSeg()
    if not disp.ok:
        return
    threading.Thread(target=disp.run, daemon=True).start()  # multiplex driver
    blink = False
    while True:
        with state_lock:
            fire = state.get("fire", 0)
            temp = state.get("temp", 0)
            connected = state.get("source") == "live"
        if not connected:
            disp.set_value("----", -1)
        elif fire:
            blink = not blink
            disp.set_value("FirE" if blink else "    ", -1)  # blink for alarm
        else:
            text, dp = format_temp(temp)
            disp.set_value(text, dp)
        time.sleep(0.2)

# ---------------- Flask ----------------
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/state")
def api_state():
    with state_lock:
        return jsonify(dict(state))

@app.route("/api/history")
def api_history():
    limit = int(request.args.get("limit", 60))
    conn = db_conn()
    rows = conn.execute(
        "SELECT ts,temp,hum,light FROM readings ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    rows.reverse()
    return jsonify([
        {"ts": r[0], "temp": r[1], "hum": r[2], "light": r[3]} for r in rows
    ])

@app.route("/api/control", methods=["POST"])
def api_control():
    d = request.get_json(silent=True) or {}
    action = d.get("action")
    cmds = {
        "led_on": "LED:1", "led_off": "LED:0",
        "vent_open": "VENT:1", "vent_close": "VENT:0",
        "mode_auto": "MODE:AUTO", "mode_manual": "MODE:MANUAL",
    }
    if action in cmds:
        queue_cmd(cmds[action])
        return jsonify({"ok": True, "sent": cmds[action]})
    if action == "set_threshold":
        if "temp" in d:  queue_cmd(f"TH_TEMP:{float(d['temp'])}")
        if "light" in d: queue_cmd(f"TH_LIGHT:{int(d['light'])}")
        if "fire" in d:  queue_cmd(f"TH_FIRE:{float(d['fire'])}")
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "unknown action"}), 400

if __name__ == "__main__":
    init_db()
    threading.Thread(target=serial_loop, daemon=True).start()
    threading.Thread(target=sevenseg_loop, daemon=True).start()  # Pi-driven 4-digit
    app.run(host="0.0.0.0", port=APP_PORT, debug=False, use_reloader=False)
