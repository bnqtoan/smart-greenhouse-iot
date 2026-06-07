# 📦 DELIVERABLE — Smart Greenhouse (IAD591 Final)

Thư mục này chứa MỌI THỨ cần nộp. Đối chiếu theo yêu cầu đề bài.

## Checklist nộp bài

| # | Yêu cầu đề bài | File | Trạng thái |
|---|---|---|---|
| 1 | **Source Code (.zip)** | `01-source-code.zip` | ✅ XONG |
| 2 | **Báo cáo slide (10, PDF)** | `02-report/Smart-Greenhouse-Slides.pdf` | ✅ XONG (10 slide, có kiến trúc + schema CSDL) |
| 3a | **Screenshot dashboard** | `03-screenshots/dashboard-bluetooth-{auto,manual}.jpg` | ✅ XONG (Live · Bluetooth) |
| 3b | **Sơ đồ đấu nối** | `03-screenshots/wiring-diagram.png` | ✅ XONG |
| 3c | **Video demo (3–7 phút)** | `05-video/demo.mp4` (4:12) + `DEMO_SCRIPT.md` | ✅ XONG |
| + | **Playbook Bluetooth** | `04-docs/BLUETOOTH_PLAYBOOK.md` | ✅ XONG |

## Tính năng nổi bật (đã chạy thật)
- 📶 **Bluetooth** Arduino→Pi (HC-05), USB backup tự động → rubric "Bluetooth (backup Serial)" mức 9–10
- 🔥 **Chống cháy/quá nhiệt**: temp ≥ ngưỡng → còi + servo mở cửa + dashboard đỏ
- 📲 **Cảnh báo Telegram từ xa** khi cháy (kênh "TheHouse")
- 🌡️ DHT22 + LDR, LED, Servo, LCD1602; Flask + SQLite + dashboard chart

## Nội dung từng file

### 01-source-code.zip
- `arduino/greenhouse/greenhouse.ino` — code Arduino (DHT22, LDR, LED, Servo, LCD)
- `rpi/app.py` — Flask + SQLite + đọc serial
- `rpi/templates/index.html` — dashboard
- `rpi/requirements.txt` — thư viện Python
- `sample_data/sensor_log_sample.csv` — log dữ liệu thật (minh chứng lưu trữ)

### 02-report/
- `Smart-Greenhouse-Slides.pdf` — **slide báo cáo 10 trang (16:9)**, nộp file này.
  Có: bìa (FSB/Đại học FPT + 5 thành viên), kiến trúc 4 tầng, sơ đồ đấu nối,
  luồng dữ liệu, logic tự động + chống cháy, Telegram, dashboard, **schema CSDL**, rubric.
- `SLIDES_OUTLINE.md` — dàn ý gốc.
- `build_slides.py` + `cover-art.png` — script dựng slide (HTML→PDF) và ảnh bìa.

### 03-screenshots/
- `dashboard-bluetooth-auto.jpg` / `dashboard-bluetooth-manual.jpg` — dashboard **Live · Bluetooth** (AUTO & MANUAL)
- `dashboard-live.png` — ảnh cũ (Live · Arduino), giữ tham khảo
- `wiring-diagram.png` — sơ đồ đấu nối chính xác từng chân (Layer 1 + Layer 2)

### 05-video/
- `demo.mp4` — video demo chạy thật (4:12, trong khung 3–7 phút)
- `DEMO_SCRIPT.md` — kịch bản từng cảnh + lời thuyết minh tiếng Việt

## Trạng thái nộp bài
✅ **Đã đủ bộ deliverable**: source + slide PDF + 2 screenshot dashboard + sơ đồ đấu nối + video demo + playbook.
- (Tuỳ chọn tăng điểm) Layer 3: LED 4 digit 74HC595 trên Pi.

## Hệ thống đang chạy
- Dashboard trên Raspberry Pi: `http://172.16.1.103:5000`
- Trang hướng dẫn: `https://bnqtoan.github.io/smart-greenhouse-iot/`
- Repo: `https://github.com/bnqtoan/smart-greenhouse-iot`
