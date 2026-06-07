# 📦 DELIVERABLE — Smart Greenhouse (IAD591 Final)

Thư mục này chứa MỌI THỨ cần nộp. Đối chiếu theo yêu cầu đề bài.

## Checklist nộp bài

| # | Yêu cầu đề bài | File | Trạng thái |
|---|---|---|---|
| 1 | **Source Code (.zip)** | `01-source-code.zip` | ✅ XONG |
| 2 | **Báo cáo slide (8–10, PPTX/PDF)** | `02-report/SLIDES_OUTLINE.md` | ⚠️ MỚI CÓ DÀN Ý — cần làm slide thật |
| 3a | **Screenshot dashboard** | `03-screenshots/dashboard-live.png` | ✅ XONG |
| 3b | **Sơ đồ đấu nối** | `03-screenshots/wiring-diagram.png` | ✅ XONG |
| 3c | **Video demo (3–7 phút)** | _(chưa quay)_ | ❌ CẦN QUAY |
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
- `SLIDES_OUTLINE.md` — dàn ý 10 slide + bảng đối chiếu rubric.
  → Cần chuyển thành PPTX/PDF (8–10 slide) trước khi nộp.

### 03-screenshots/
- `dashboard-live.png` — ảnh dashboard đang chạy (Live · Arduino)
- `wiring-diagram.png` — sơ đồ đấu nối chính xác từng chân (Layer 1 + Layer 2)

## Còn phải làm trước khi nộp
1. **Slide báo cáo** — từ `02-report/SLIDES_OUTLINE.md` → xuất PPTX/PDF.
2. **Video demo 3–7 phút** — quay: phần cứng → cảm biến đổi giá trị → dashboard Live →
   điều khiển LED/cửa → đổi Auto/Manual → mở SQLite cho thấy log.
3. (Tuỳ chọn tăng điểm) Layer 3: LED 4 digit + Bluetooth.

## Hệ thống đang chạy
- Dashboard trên Raspberry Pi: `http://172.16.1.103:5000`
- Trang hướng dẫn: `https://bnqtoan.github.io/smart-greenhouse-iot/`
- Repo: `https://github.com/bnqtoan/smart-greenhouse-iot`
