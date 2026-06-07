"""
Smart Greenhouse - Raspberry Pi (Gateway + Application Layer)
IAD591 Final Project

Reads JSON lines from Arduino over USB (/dev/ttyACM0), stores in SQLite,
serves a Flask dashboard, and sends control commands back to Arduino.

Reliability design (lab hardware is flaky):
  - Serial runs in a background thread; main web app never blocks on it.
  - If the Arduino is not connected, falls back to SIMULATED data so the
    dashboard + chart + controls still demo perfectly. A status flag tells
    the UI whether data is live or simulated.
  - All DB writes are wrapped; a bad reading never crashes the server.

Run:  python3 app.py     then open http://<pi-ip>:5000
"""
import json
import sqlite3
import threading
import time
import math
import os
from datetime import datetime
from flask import Flask, jsonify, request, render_template

# ---------------- config ----------------
SERIAL_PORT = "/dev/ttyACM0"   # Arduino over USB. (Try /dev/ttyACM1 or /dev/ttyUSB0 if needed)
BAUD_RATE   = 9600
DB_PATH     = os.path.join(os.path.dirname(__file__), "greenhouse.db")
APP_PORT    = 5000

# ---------------- shared state ----------------
state = {
    "temp": 0.0, "hum": 0.0, "light": 0,
    "led": 0, "vent": 0, "mode": "auto",
    "source": "starting",      # "live" | "simulated"
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

# ---------------- serial / simulation thread ----------------
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

def serial_loop():
    """Try real Arduino first; if unavailable, run simulator. Auto-reconnect."""
    last_save = 0
    while True:
        ser = None
        try:
            import serial  # pyserial
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)  # let Arduino reset after USB connect
            print(f"[serial] connected {SERIAL_PORT}")
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
                    "mode": d.get("mode", "auto"),
                }
                update_state(clean, "live")
                now = time.time()
                if now - last_save >= 2:   # log every 2s
                    save_reading(clean)
                    last_save = now
        except Exception as e:
            print(f"[serial] not available ({e}) -> SIMULATED mode")
            if ser:
                try: ser.close()
                except: pass
            run_simulator()  # blocks until a real port appears? no -> returns periodically
        time.sleep(3)  # then retry real serial

def run_simulator():
    """Generate believable data so the demo never shows a blank dashboard.
    Honors mode + commands so controls still 'work' visually."""
    last_save = 0
    t0 = time.time()
    sim = {"led": 0, "vent": 0, "mode": "auto"}
    th_temp, th_light = 30.0, 400
    # run simulator for ~5s bursts, then return so serial_loop can re-probe the port
    end = time.time() + 5
    while time.time() < end:
        # apply queued commands to the simulated arduino
        with cmd_lock:
            cmds = pending_cmd[:]
            pending_cmd.clear()
        for c in cmds:
            if c == "LED:1": sim["led"], sim["mode"] = 1, "manual"
            elif c == "LED:0": sim["led"], sim["mode"] = 0, "manual"
            elif c == "VENT:1": sim["vent"], sim["mode"] = 1, "manual"
            elif c == "VENT:0": sim["vent"], sim["mode"] = 0, "manual"
            elif c == "MODE:AUTO": sim["mode"] = "auto"
            elif c == "MODE:MANUAL": sim["mode"] = "manual"
            elif c.startswith("TH_TEMP:"): th_temp = float(c[8:] or 30)
            elif c.startswith("TH_LIGHT:"): th_light = int(c[9:] or 400)

        elapsed = time.time() - t0
        temp = 26 + 4 * math.sin(elapsed / 8.0)        # 22..30 C
        hum = 60 + 10 * math.sin(elapsed / 11.0)       # 50..70 %
        light = int(500 + 300 * math.sin(elapsed / 6.0))  # 200..800
        if sim["mode"] == "auto":
            sim["led"] = 1 if light < th_light else 0
            sim["vent"] = 1 if temp > th_temp else 0
        d = {"temp": round(temp, 1), "hum": round(hum, 1), "light": light,
             "led": sim["led"], "vent": sim["vent"], "mode": sim["mode"]}
        update_state(d, "simulated")
        now = time.time()
        if now - last_save >= 2:
            save_reading(d)
            last_save = now
        time.sleep(1)

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
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "unknown action"}), 400

if __name__ == "__main__":
    init_db()
    threading.Thread(target=serial_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=APP_PORT, debug=False, use_reloader=False)
