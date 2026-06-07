"""
Telegram fire-alarm notifier — sends a message to Telegram when fire is detected.

Real-IoT value: the greenhouse warns the owner REMOTELY (phone) the instant a
fire/overheat is detected, even if nobody is watching the dashboard.

Config: reads rpi/telegram_config.json  (GIT-IGNORED — keeps the bot token secret)
    {
      "token":   "123456:ABC...",
      "chat_id": "123456789"
    }
If the file is missing/invalid, the notifier silently disables itself and the
rest of the app runs normally.

Behavior:
  - On fire 0 -> 1 : send "🔥 FIRE ALERT" with temp.
  - On fire 1 -> 0 : send "✅ All clear".
  - Edge-triggered: one message per transition (no spam).
"""
import json
import os
import threading
import urllib.parse
import urllib.request

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "telegram_config.json")


class TelegramNotifier:
    def __init__(self):
        self.ok = False
        self.token = None
        self.chat_id = None
        self._last_fire = 0
        try:
            with open(CONFIG_PATH) as f:
                cfg = json.load(f)
            self.token = cfg["token"]
            self.chat_id = str(cfg["chat_id"])
            if self.token and self.chat_id:
                self.ok = True
                print("[telegram] notifier enabled")
        except Exception as e:
            print(f"[telegram] disabled ({e}) — add telegram_config.json to enable")

    def _send(self, text):
        if not self.ok:
            return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
        }).encode()
        try:
            urllib.request.urlopen(url, data=data, timeout=8).read()
        except Exception as e:
            print(f"[telegram] send failed: {e}")

    def send_async(self, text):
        """Fire-and-forget so the serial/web loop never blocks on the network."""
        threading.Thread(target=self._send, args=(text,), daemon=True).start()

    def on_state(self, fire, temp):
        """Call every cycle with current fire flag + temp. Sends only on change."""
        fire = 1 if fire else 0
        if fire and not self._last_fire:
            self.send_async(
                f"🔥 <b>CẢNH BÁO CHÁY / QUÁ NHIỆT</b>\n"
                f"Nhà kính phát hiện nhiệt độ nguy hiểm: <b>{temp:.1f}°C</b>\n"
                f"Còi báo động đã kêu, cửa thông gió đã mở tự động."
            )
        elif not fire and self._last_fire:
            self.send_async(
                f"✅ <b>Đã an toàn</b>\nNhiệt độ trở lại bình thường: <b>{temp:.1f}°C</b>"
            )
        self._last_fire = fire

    def send_test(self):
        self.send_async("✅ Bot kết nối thành công — Smart Greenhouse sẵn sàng gửi cảnh báo cháy.")
