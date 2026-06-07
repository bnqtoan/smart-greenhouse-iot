#!/usr/bin/env python3
# Build the Smart Greenhouse report deck (HTML -> PDF via Chrome).
import base64, os, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SHOTS = ROOT / "deliverable" / "03-screenshots"

def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

dash_auto = b64(SHOTS / "dashboard-bluetooth-auto.jpg")
dash_manual = b64(SHOTS / "dashboard-bluetooth-manual.jpg")
wiring = b64(SHOTS / "wiring-diagram.png")
lcd_fire = b64(SHOTS / "lcd-fire-alarm.jpg")
lcd_normal = b64(SHOTS / "lcd-normal.jpg")
telegram = b64(SHOTS / "telegram-alerts.jpg")
cover_art = b64(pathlib.Path(__file__).parent / "cover-art.png")

TEAM = [
    "Bùi Nguyễn Quốc Toàn",
    "Mã Ngọc Long Bảo",
    "Nguyễn Thị Hương",
    "Lê Nguyễn Gia Bảo",
    "Phạm Xuân Thắng",
]
team_rows = "".join(f"<li>{n}</li>" for n in TEAM)

# ---- Architecture diagram (4-layer) as inline SVG ----
ARCH_SVG = """
<svg viewBox="0 0 1180 250" xmlns="http://www.w3.org/2000/svg" class="arch">
  <defs>
    <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1b2a4a"/><stop offset="1" stop-color="#101a30"/>
    </linearGradient>
    <marker id="arr" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto">
      <path d="M0,0 L7,3 L0,6 Z" fill="#6ee7b7"/>
    </marker>
  </defs>
  <!-- boxes -->
  <g font-family="Inter,Arial" text-anchor="middle">
    <rect x="20"  y="60" width="220" height="130" rx="16" fill="url(#g1)" stroke="#33507f"/>
    <text x="130" y="92"  fill="#6ee7b7" font-size="15" font-weight="700">LAYER 1 · DEVICE</text>
    <text x="130" y="118" fill="#fff" font-size="18" font-weight="700">Arduino UNO</text>
    <text x="130" y="142" fill="#9fb3d0" font-size="13">DHT22 · LDR · LED</text>
    <text x="130" y="162" fill="#9fb3d0" font-size="13">Servo · Buzzer · LCD</text>

    <rect x="320" y="60" width="220" height="130" rx="16" fill="url(#g1)" stroke="#33507f"/>
    <text x="430" y="92"  fill="#7dd3fc" font-size="15" font-weight="700">LAYER 2 · GATEWAY</text>
    <text x="430" y="118" fill="#fff" font-size="18" font-weight="700">Raspberry Pi</text>
    <text x="430" y="142" fill="#9fb3d0" font-size="13">đọc serial · ghi DB</text>
    <text x="430" y="162" fill="#9fb3d0" font-size="13">systemd service</text>

    <rect x="620" y="60" width="220" height="130" rx="16" fill="url(#g1)" stroke="#33507f"/>
    <text x="730" y="92"  fill="#c4b5fd" font-size="15" font-weight="700">LAYER 3 · APP</text>
    <text x="730" y="118" fill="#fff" font-size="18" font-weight="700">Flask + SQLite</text>
    <text x="730" y="142" fill="#9fb3d0" font-size="13">dashboard realtime</text>
    <text x="730" y="162" fill="#9fb3d0" font-size="13">REST API · điều khiển</text>

    <rect x="920" y="60" width="220" height="130" rx="16" fill="url(#g1)" stroke="#f0883e"/>
    <text x="1030" y="92"  fill="#f0883e" font-size="15" font-weight="700">LAYER 4 · ALERT</text>
    <text x="1030" y="118" fill="#fff" font-size="18" font-weight="700">Telegram</text>
    <text x="1030" y="142" fill="#9fb3d0" font-size="13">cảnh báo từ xa</text>
    <text x="1030" y="162" fill="#9fb3d0" font-size="13">kênh "TheHouse"</text>

    <!-- arrows -->
    <line x1="242" y1="125" x2="316" y2="125" stroke="#6ee7b7" stroke-width="2.5" marker-end="url(#arr)"/>
    <line x1="542" y1="125" x2="616" y2="125" stroke="#6ee7b7" stroke-width="2.5" marker-end="url(#arr)"/>
    <line x1="842" y1="125" x2="916" y2="125" stroke="#6ee7b7" stroke-width="2.5" marker-end="url(#arr)"/>
    <text x="279" y="48" fill="#6ee7b7" font-size="13" font-weight="700">Bluetooth HC-05</text>
    <text x="279" y="205" fill="#7a8aa5" font-size="11">(USB backup tự động)</text>
    <text x="579" y="48" fill="#9fb3d0" font-size="12">SQLite</text>
    <text x="879" y="48" fill="#f0883e" font-size="12">khi cháy 🔥</text>
  </g>
</svg>
"""

# ---- DB schema diagram as inline SVG ----
DB_SVG = """
<svg viewBox="0 0 560 380" xmlns="http://www.w3.org/2000/svg" class="dbsvg">
  <rect x="30" y="20" width="500" height="48" rx="10" fill="#7c3aed"/>
  <text x="280" y="51" text-anchor="middle" fill="#fff" font-family="Inter,Arial" font-size="20" font-weight="700">readings</text>
  <g font-family="JetBrains Mono,monospace" font-size="15">
    <!-- rows -->
    <rect x="30" y="68"  width="500" height="38" fill="#16203a"/>
    <rect x="30" y="106" width="500" height="38" fill="#101a30"/>
    <rect x="30" y="144" width="500" height="38" fill="#16203a"/>
    <rect x="30" y="182" width="500" height="38" fill="#101a30"/>
    <rect x="30" y="220" width="500" height="38" fill="#16203a"/>
    <rect x="30" y="258" width="500" height="38" fill="#101a30"/>
    <rect x="30" y="296" width="500" height="38" fill="#16203a"/>
    <rect x="30" y="334" width="500" height="38" fill="#101a30"/>

    <text x="48" y="93"  fill="#f0883e" font-weight="700">🔑 id</text>
    <text x="300" y="93" fill="#9fb3d0">INTEGER · PK AUTOINCREMENT</text>
    <text x="48" y="131" fill="#7dd3fc">ts</text>
    <text x="300" y="131" fill="#9fb3d0">TEXT · ISO timestamp</text>
    <text x="48" y="169" fill="#6ee7b7">temp</text>
    <text x="300" y="169" fill="#9fb3d0">REAL · °C (DHT22)</text>
    <text x="48" y="207" fill="#6ee7b7">hum</text>
    <text x="300" y="207" fill="#9fb3d0">REAL · % (DHT22)</text>
    <text x="48" y="245" fill="#6ee7b7">light</text>
    <text x="300" y="245" fill="#9fb3d0">INTEGER · lux thô (LDR)</text>
    <text x="48" y="283" fill="#c4b5fd">led</text>
    <text x="300" y="283" fill="#9fb3d0">INTEGER · 0/1 đèn</text>
    <text x="48" y="321" fill="#c4b5fd">vent</text>
    <text x="300" y="321" fill="#9fb3d0">INTEGER · 0/1 cửa</text>
    <text x="48" y="359" fill="#c4b5fd">mode</text>
    <text x="300" y="359" fill="#9fb3d0">TEXT · auto / manual</text>
  </g>
</svg>
"""

SLIDES = []

def slide(html, cls=""):
    SLIDES.append(f'<section class="slide {cls}">{html}</section>')

# 1 — Cover
slide(f"""
  <img class="cover-bg" src="data:image/png;base64,{cover_art}"/>
  <div class="cover-grad"></div>
  <div class="cover">
    <div class="school">Viện Quản trị & Công nghệ FSB · Đại học FPT</div>
    <h1>Smart Greenhouse</h1>
    <div class="tagline">Nhà kính tự động: <b>giám sát – bảo vệ – cảnh báo từ xa</b></div>
    <div class="course">IAD591 · Internet of Things · Đồ án cuối kỳ</div>
    <ul class="team">{team_rows}</ul>
  </div>
""", "cover-slide")

# 2 — Intro
slide("""
  <h2>Giới thiệu hệ thống</h2>
  <div class="two">
    <div>
      <h3>Bài toán</h3>
      <p>Giám sát & tự động hoá một nhà kính mini: đo môi trường, tự điều khiển thiết bị,
      và <b>chủ động bảo vệ cây trồng</b> khi có sự cố.</p>
      <h3>Mục tiêu</h3>
      <ul>
        <li>Đo nhiệt độ, độ ẩm, ánh sáng realtime</li>
        <li>Tự bật đèn trồng cây & mở cửa thông gió</li>
        <li>Dashboard điều khiển từ xa (Auto/Manual)</li>
        <li><b>Tự bảo vệ khi quá nhiệt / cháy</b></li>
        <li><b>Báo động Telegram tới điện thoại</b></li>
      </ul>
    </div>
    <div class="story-card">
      <div class="big">Không chỉ<br><span class="g">GIÁM SÁT</span></div>
      <div class="plus">+ <b>BẢO VỆ</b> (chống cháy)</div>
      <div class="plus">+ <b>CẢNH BÁO TỪ XA</b> (Telegram)</div>
    </div>
  </div>
""")

# 3 — Architecture
slide(f"""
  <h2>Kiến trúc 4 tầng</h2>
  {ARCH_SVG}
  <p class="cap">Truyền <b>không dây qua Bluetooth HC-05</b> (/dev/rfcomm0). Rớt Bluetooth → tự
  fallback sang USB ⇒ hệ thống <b>luôn online</b>. Sự kiện cháy đẩy thẳng lên Telegram.</p>
""")

# 4 — Hardware / wiring
slide(f"""
  <h2>Sơ đồ phần cứng & đấu nối</h2>
  <div class="two wide-left">
    <img class="shot" src="data:image/png;base64,{wiring}"/>
    <div>
      <table class="pins">
        <tr><th>Linh kiện</th><th>Chân</th></tr>
        <tr><td>DHT22 (nhiệt + ẩm)</td><td>D2</td></tr>
        <tr><td>LDR (ánh sáng)</td><td>A0</td></tr>
        <tr><td>LED trồng cây</td><td>D7</td></tr>
        <tr><td>Servo cửa thông gió</td><td>D9</td></tr>
        <tr><td>Buzzer báo cháy</td><td>D8</td></tr>
        <tr><td>LCD1602 I2C</td><td>A4 / A5</td></tr>
        <tr><td>HC-05 Bluetooth</td><td>D10/D11</td></tr>
      </table>
      <figure class="lcd-thumb"><img class="shot" src="data:image/jpeg;base64,{lcd_normal}"/><figcaption>Mạch thật: LCD hiển thị T/H, chế độ MANUAL</figcaption></figure>
    </div>
  </div>
""")

# 5 — Data flow
slide("""
  <h2>Luồng dữ liệu</h2>
  <div class="flow">
    <div class="fbox">Cảm biến<br><small>DHT22 · LDR</small></div><span>→</span>
    <div class="fbox">Arduino<br><small>đóng gói JSON</small></div><span>→</span>
    <div class="fbox bt">Bluetooth<br><small>USB backup</small></div><span>→</span>
    <div class="fbox">Pi<br><small>đọc serial</small></div><span>→</span>
    <div class="fbox">SQLite<br><small>readings</small></div><span>→</span>
    <div class="fbox">API<br><small>Flask</small></div><span>→</span>
    <div class="fbox">Dashboard</div>
  </div>
  <div class="flow back">
    <div class="fbox">Web (lệnh)</div><span>→</span>
    <div class="fbox">Pi</div><span>→</span>
    <div class="fbox">Arduino<br><small>LED · VENT · MODE · ngưỡng</small></div>
    <div class="fire">🔥 Sự kiện cháy → Pi → <b>Telegram</b></div>
  </div>
""")

# 6 — Automation + protection
slide(f"""
  <h2>Logic tự động + BẢO VỆ</h2>
  <div class="three">
    <div>
      <h3>Tự động hoá</h3>
      <ul>
        <li>Đèn <b>bật khi tối</b> (light &lt; ngưỡng)</li>
        <li>Cửa <b>mở khi nóng</b> (temp &gt; ngưỡng)</li>
        <li>Chế độ <b>Auto / Manual</b> chuyển tức thì</li>
        <li>Ngưỡng chỉnh được từ dashboard</li>
      </ul>
    </div>
    <div class="fire-card">
      <div class="fhead">🔥 FIRE / OVERHEAT</div>
      <div class="fsub">killer feature</div>
      <p>Khi <b>temp ≥ ngưỡng</b>, tự động:</p>
      <ul>
        <li>🔊 Buzzer hú</li>
        <li>🚪 Servo mở cửa thoát nhiệt</li>
        <li>🟥 Banner đỏ dashboard</li>
        <li>📲 Alert Telegram</li>
      </ul>
    </div>
    <figure><img class="shot" src="data:image/jpeg;base64,{lcd_fire}"/><figcaption>LCD báo cháy thật: "!! FIRE ALARM !" · VENT OP</figcaption></figure>
  </div>
""")

# 7 — Telegram remote alert
slide(f"""
  <h2>Cảnh báo từ xa — Telegram (Layer 4)</h2>
  <div class="tg-layout">
    <div>
      <p>Khi xảy ra <b>cháy / quá nhiệt</b>, Pi gửi cảnh báo lên kênh Telegram
      <b>"TheHouse"</b> với giá trị IoT thật.</p>
      <ul>
        <li>Người dùng nhận thông báo <b>ngay trên điện thoại</b></li>
        <li>Không cần mở dashboard vẫn biết sự cố</li>
        <li>Tự gửi <b>"✅ Đã an toàn"</b> khi nhiệt độ về bình thường</li>
        <li>Đóng vòng lặp: <b>giám sát → bảo vệ → báo người</b></li>
      </ul>
      <p class="proof">📲 Ảnh thật từ kênh <b>TheHouse</b>: nhiều lần cháy được phát hiện,
      còi kêu + cửa tự mở, kèm thông báo "đã an toàn".</p>
    </div>
    <figure class="phone"><img class="shot" src="data:image/jpeg;base64,{telegram}"/></figure>
  </div>
""")

# 8 — Dashboard screenshots
slide(f"""
  <h2>Dashboard (chạy thật · Live Bluetooth)</h2>
  <div class="two even">
    <figure><img class="shot" src="data:image/jpeg;base64,{dash_auto}"/><figcaption>Chế độ AUTO</figcaption></figure>
    <figure><img class="shot" src="data:image/jpeg;base64,{dash_manual}"/><figcaption>Chế độ MANUAL — công tắc tay</figcaption></figure>
  </div>
  <p class="cap">UI dark glassmorphism · metric cards · chart realtime (Chart.js) · công tắc LED/Vent/Mode ·
  đặt ngưỡng · trạng thái <b>"Live · Bluetooth"</b>. Đủ rubric: hiện tại + lịch sử + chart + điều khiển.</p>
""")

# 9 — DB schema + deployment
slide(f"""
  <h2>Thiết kế CSDL & Triển khai</h2>
  <div class="two wide-right">
    {DB_SVG}
    <div>
      <h3>Lưu trữ — SQLite</h3>
      <p>Bảng <code>readings</code> ghi mỗi lần đọc cảm biến: môi trường + trạng thái thiết bị + chế độ.
      Dùng cho chart lịch sử và minh chứng lưu trữ.</p>
      <h3>Triển khai</h3>
      <ul>
        <li>Chạy thật trên <b>Raspberry Pi</b></li>
        <li><b>systemd service</b> tự khởi động khi boot</li>
        <li>Mã nguồn quản lý bằng Git, có trang hướng dẫn web</li>
      </ul>
    </div>
  </div>
""")

# 10 — Rubric + conclusion
RUBRIC = [
    ("Arduino", "≥2 cảm biến + LCD + actuator", "DHT22+LDR + LCD1602 + LED+Servo+Buzzer ✅"),
    ("Giao tiếp", "Bluetooth (backup Serial)", "HC-05 /dev/rfcomm0 + USB auto-backup ✅ <b>mức cao nhất</b>"),
    ("Raspberry Pi", "Flask dashboard + điều khiển", "✅"),
    ("Lưu dữ liệu", "SQLite", "✅ bảng readings"),
    ("Dashboard", "hiện tại + lịch sử + chart", "✅ dark UI + Chart.js"),
    ("Điều khiển GUI", "bắt buộc", "LED/Vent/Mode/Ngưỡng ✅"),
    ("Bonus", "sáng tạo", "🔥 Fire protection + 📲 Telegram + systemd + Pages ✅"),
]
rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a,b,c in RUBRIC)
slide(f"""
  <h2>Kết quả & Kết luận</h2>
  <table class="rubric">
    <tr><th>Tiêu chí</th><th>Mức 9–10</th><th>Đã đạt</th></tr>
    {rows}
  </table>
  <p class="cap">Đã làm: <b>giám sát + tự động + chống cháy + cảnh báo Telegram</b>, chạy thật trên phần cứng.
  Mở rộng: thêm cảm biến · cloud · app mobile.</p>
""")

SLIDE_HTML = "\n".join(SLIDES)

DOC = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<style>
@page {{ size: 1280px 720px; margin: 0; }}
* {{ box-sizing: border-box; margin:0; padding:0; }}
body {{ font-family: Inter, -apple-system, "Segoe UI", Arial, sans-serif; }}
.slide {{
  width: 1280px; height: 720px; padding: 54px 64px;
  background: radial-gradient(1200px 600px at 80% -10%, #16243f 0%, #0a1120 55%);
  color: #e7eefc; position: relative; page-break-after: always; overflow: hidden;
}}
.slide::after {{ content:"Smart Greenhouse · IAD591"; position:absolute; bottom:22px; right:40px;
  font-size:13px; color:#5b6b88; }}
h2 {{ font-size: 40px; font-weight: 800; margin-bottom: 26px; color:#fff;
  border-left: 6px solid #6ee7b7; padding-left: 18px; }}
h3 {{ font-size: 21px; color:#7dd3fc; margin: 16px 0 8px; }}
p {{ font-size: 19px; line-height: 1.55; color:#c9d6ec; margin: 8px 0; }}
ul {{ margin: 6px 0 6px 24px; }}
li {{ font-size: 19px; line-height: 1.7; color:#c9d6ec; }}
b {{ color:#fff; }}
code {{ font-family: "JetBrains Mono", monospace; background:#16203a; padding:2px 7px; border-radius:6px; color:#7dd3fc; }}
.cap {{ position:absolute; bottom:54px; left:64px; right:64px; font-size:15px; color:#90a2c2; }}
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:34px; align-items:start; }}
.two.wide-left {{ grid-template-columns: 1.45fr 1fr; }}
.two.wide-right {{ grid-template-columns: 1fr 1.2fr; align-items:center; }}
.two.even {{ grid-template-columns:1fr 1fr; gap:26px; }}
.three {{ display:grid; grid-template-columns:1fr 1fr 0.85fr; gap:24px; align-items:start; }}
.three h3 {{ margin-top:0; }}
.three li {{ font-size:17px; line-height:1.55; }}
.lcd-thumb {{ margin-top:16px; }}
.lcd-thumb img {{ border-radius:10px; }}
.lcd-thumb figcaption {{ font-size:13px; margin-top:7px; }}
.three figcaption {{ font-size:14px; }}
.tg-layout {{ display:grid; grid-template-columns:1.45fr 0.55fr; gap:40px; align-items:start; }}
.phone img {{ width:100%; border-radius:14px; max-height:540px; object-fit:contain; }}
.proof {{ margin-top:18px; font-size:16px; color:#9fe7c8; border-left:3px solid #6ee7b7; padding-left:14px; }}
.shot {{ width:100%; border-radius:12px; border:1px solid #25364f; box-shadow:0 14px 40px rgba(0,0,0,.5); }}
figure {{ margin:0; }} figcaption {{ text-align:center; margin-top:10px; font-size:16px; color:#9fb3d0; }}

/* cover */
.cover-slide {{ display:flex; align-items:flex-start; justify-content:center; padding:64px; }}
.cover-slide::after {{ content:none; }}
.cover-bg {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; z-index:0; }}
.cover-grad {{ position:absolute; inset:0; z-index:1;
  background:linear-gradient(180deg, rgba(8,14,28,.72) 0%, rgba(8,14,28,.25) 42%, rgba(8,14,28,.85) 100%); }}
.cover {{ position:relative; z-index:2; text-align:center; margin-top:40px; }}
.cover .school {{ font-size:18px; color:#9fe7c8; letter-spacing:.5px; margin-bottom:14px;
  text-shadow:0 2px 12px rgba(0,0,0,.8); }}
.cover h1 {{ font-size:80px; font-weight:900; letter-spacing:-1px;
  background:linear-gradient(90deg,#6ee7b7,#7dd3fc,#c4b5fd); -webkit-background-clip:text; color:transparent;
  filter: drop-shadow(0 4px 24px rgba(0,0,0,.6)); }}
.cover .tagline {{ font-size:25px; color:#eaf2ff; margin-top:12px; text-shadow:0 2px 12px rgba(0,0,0,.85); }}
.cover .course {{ font-size:18px; color:#7dd3fc; margin-top:22px; letter-spacing:.5px; text-shadow:0 2px 10px rgba(0,0,0,.8); }}
.cover .team {{ list-style:none; margin:20px auto 0; display:flex; gap:10px 22px; flex-wrap:wrap; justify-content:center; max-width:780px; }}
.cover .team li {{ font-size:17px; color:#eaf2ff; background:rgba(16,26,48,.7); padding:8px 18px; border-radius:30px; border:1px solid #2a3c58; backdrop-filter:blur(4px); }}
.cover .repo {{ margin-top:22px; font-family:"JetBrains Mono",monospace; font-size:16px; color:#6ee7b7; text-shadow:0 2px 10px rgba(0,0,0,.8); }}

/* intro story */
.story-card {{ background:linear-gradient(160deg,#15233f,#0d1626); border:1px solid #2a3c58; border-radius:18px; padding:32px; }}
.story-card .big {{ font-size:34px; font-weight:800; line-height:1.2; }}
.story-card .g {{ background:linear-gradient(90deg,#6ee7b7,#7dd3fc); -webkit-background-clip:text; color:transparent; }}
.story-card .plus {{ font-size:23px; margin-top:18px; color:#f0883e; }}

/* arch + db svg */
.arch {{ width:100%; height:auto; margin-top:6px; }}
.dbsvg {{ width:88%; height:auto; }}

/* flow */
.flow {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin:18px 0; }}
.flow.back {{ margin-top:30px; }}
.fbox {{ background:#15233f; border:1px solid #2a3c58; border-radius:12px; padding:14px 16px; font-size:17px; font-weight:700; text-align:center; color:#fff; }}
.fbox small {{ display:block; font-weight:400; font-size:13px; color:#9fb3d0; margin-top:3px; }}
.fbox.bt {{ border-color:#6ee7b7; color:#6ee7b7; }}
.flow span {{ color:#6ee7b7; font-size:22px; font-weight:700; }}
.fire {{ margin-left:auto; background:#2a1410; border:1px solid #f0883e; color:#f0883e; padding:14px 18px; border-radius:12px; font-size:17px; }}

/* pins / rubric tables */
table.pins, table.rubric {{ border-collapse:collapse; width:100%; }}
table.pins td, table.pins th {{ border:1px solid #2a3c58; padding:9px 14px; font-size:17px; text-align:left; }}
table.pins th {{ background:#16203a; color:#7dd3fc; }}
table.rubric th, table.rubric td {{ border:1px solid #2a3c58; padding:11px 16px; font-size:16px; text-align:left; }}
table.rubric th {{ background:#7c3aed; color:#fff; }}
table.rubric tr:nth-child(even) td {{ background:#101a30; }}

/* fire card */
.fire-card {{ background:linear-gradient(160deg,#2a1410,#1a0d0a); border:1px solid #f0883e; border-radius:18px; padding:22px; }}
.fire-card p {{ font-size:16px; }}
.three .fire-card li {{ color:#f3d9c9; }}
.fire-card .fhead {{ font-size:20px; font-weight:800; color:#f0883e; }}
.fire-card .fsub {{ font-size:14px; color:#c98a6a; margin-bottom:10px; letter-spacing:1px; }}
.fire-card ul li {{ color:#f3d9c9; }}

/* telegram card */
.tg-card {{ background:#0e1726; border:1px solid #2a3c58; border-radius:18px; padding:0; overflow:hidden; }}
.tg-head {{ background:#229ed9; color:#fff; font-weight:800; font-size:20px; padding:16px 22px; }}
.tg-msg {{ padding:22px; font-size:19px; line-height:1.7; color:#e7eefc; background:#17212b; margin:18px; border-radius:14px; }}
</style></head><body>
{SLIDE_HTML}
</body></html>"""

OUT_HTML = pathlib.Path(__file__).parent / "Smart-Greenhouse-Slides.html"
OUT_HTML.write_text(DOC, encoding="utf-8")
print("wrote", OUT_HTML)
