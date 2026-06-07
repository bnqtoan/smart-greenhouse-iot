# Kịch bản video demo — Smart Greenhouse (3–7 phút)

> File quay: `demo.mp4` (4:12). Kịch bản dưới = thứ tự cảnh + lời thuyết minh tiếng Việt.

## 0:00 — Mở đầu (15s)
"Đây là Smart Greenhouse — nhà kính tự động nhóm IAD591. Hệ thống không chỉ **giám sát**,
mà còn **tự bảo vệ chống cháy** và **cảnh báo từ xa qua Telegram**."
→ Quay tổng thể phần cứng: Arduino + breadboard + nhà kính mini.

## 0:15 — Phần cứng & cảm biến (40s)
- Chỉ từng linh kiện: DHT22 (nhiệt+ẩm), LDR (sáng), LED, Servo cửa, Buzzer, LCD, HC-05.
- **Che LDR** bằng tay → số ánh sáng trên LCD/dashboard giảm.
- **Hà hơi vào DHT22** → nhiệt độ & độ ẩm tăng.

## 0:55 — Truyền Bluetooth (KEY) (40s)
- Show dashboard trạng thái **"Live · Bluetooth"**.
- "Dữ liệu truyền không dây qua HC-05 trên /dev/rfcomm0."
- **Rút cáp USB** → dashboard vẫn chạy, vẫn "Live · Bluetooth" ⇒ chứng minh không dây thật.
- (Tuỳ chọn) tắt Bluetooth → tự fallback USB, vẫn online.

## 1:35 — Dashboard realtime (40s)
- Chart cập nhật realtime (nhiệt/ẩm/sáng).
- Metric cards đổi giá trị theo cảm biến.
- Footer: Arduino → Bluetooth → Pi → Flask+SQLite.

## 2:15 — Điều khiển & Auto/Manual (40s)
- Chế độ **AUTO**: che LDR → đèn tự bật; tăng nhiệt → cửa tự mở.
- Chuyển **MANUAL**: bấm công tắc LED / Cửa thông gió trên web → thiết bị phản hồi ngay.
- Đổi **ngưỡng** nhiệt/sáng → Áp dụng.

## 2:55 — BẢO VỆ chống cháy (killer feature) (45s)
- Tăng nhiệt vượt ngưỡng (bật lửa/máy sấy gần DHT22).
- **temp ≥ ngưỡng** → **Buzzer hú** + **Servo tự mở cửa thoát nhiệt** + **banner đỏ** trên dashboard.

## 3:40 — Cảnh báo Telegram từ xa (20s)
- Đưa điện thoại vào hình: thông báo từ kênh **"TheHouse"** hiện lên.
- "Dù không mở dashboard, người dùng vẫn nhận cảnh báo cháy trên điện thoại."

## 4:00 — Lưu trữ & kết (12s)
- Mở file SQLite / `sensor_log_sample.csv` cho thấy log dữ liệu thật.
- "Giám sát + tự động + chống cháy + cảnh báo từ xa — chạy thật trên Raspberry Pi."

---
**Checklist quay đủ:** phần cứng ✓ · cảm biến đổi giá trị ✓ · Bluetooth (rút USB) ✓ ·
dashboard+chart ✓ · điều khiển LED/cửa ✓ · Auto/Manual ✓ · cháy→buzzer+servo+banner ✓ ·
Telegram trên điện thoại ✓ · SQLite log ✓
