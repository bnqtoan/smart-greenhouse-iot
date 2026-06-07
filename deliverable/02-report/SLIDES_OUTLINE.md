# SLIDE OUTLINE (8–10 slide) — Smart Greenhouse

> Product story: **không chỉ GIÁM SÁT, mà còn BẢO VỆ (chống cháy) và CẢNH BÁO TỪ XA (Telegram)**.

1. **Bìa** — Smart Greenhouse · IAD591 · tên nhóm + thành viên (MSSV).
   Tagline: "Nhà kính tự động: giám sát – bảo vệ – cảnh báo từ xa".
2. **Giới thiệu hệ thống** — Bài toán: giám sát & tự động hoá nhà kính mini.
   Mục tiêu: đo nhiệt/ẩm/sáng, tự bật đèn & mở cửa thông gió, dashboard điều khiển từ xa,
   **tự bảo vệ khi quá nhiệt/cháy** và **báo động Telegram tới điện thoại**.
3. **Kiến trúc 3 tầng** — sơ đồ: Arduino (Device) → **Bluetooth HC-05** (USB backup) → Pi (Gateway) →
   Flask+SQLite (App) → **Telegram (cảnh báo từ xa)**.
   Nhấn: truyền **không dây qua Bluetooth** (/dev/rfcomm0); rớt BT thì tự fallback USB ⇒ luôn online.
4. **Sơ đồ phần cứng / đấu nối** — ảnh breadboard + bảng pin:
   DHT22 (nhiệt+ẩm), LDR (sáng), LED grow-light D7, Servo cửa thông gió D9, **Buzzer báo cháy D8**,
   LCD1602 I2C (A4/A5), HC-05 (Bluetooth). 7-seg 74HC595 trên Pi (tuỳ chọn).
5. **Luồng dữ liệu** — Arduino đọc cảm biến → JSON → **Bluetooth → Pi** (USB backup) → SQLite → API → Dashboard;
   lệnh web → Pi → Arduino (LED/VENT/MODE/threshold). Sự kiện cháy → Pi → **Telegram**.
6. **Logic tự động + BẢO VỆ** — đèn bật khi tối (light < ngưỡng); cửa mở khi nóng (temp > ngưỡng); Auto/Manual.
   **Fire/overheat protection (killer feature):** temp ≥ ngưỡng ⇒ **buzzer hú + servo tự mở cửa thoát nhiệt + banner đỏ trên dashboard**.
7. **Cảnh báo từ xa — Telegram (Layer 4)** — khi cháy, hệ thống gửi alert tới channel Telegram "TheHouse".
   Nhấn: giá trị IoT thật — người dùng nhận thông báo trên điện thoại dù không mở dashboard.
8. **Dashboard (ảnh chụp)** — UI dark glassmorphism: metric cards, chart realtime (Chart.js),
   công tắc LED/Vent/Mode, đặt ngưỡng, trạng thái **"Live · Bluetooth"**, banner cháy đỏ.
   Nhấn rubric: hiện tại + lịch sử + chart + điều khiển.
9. **Lưu trữ + Triển khai** — SQLite `readings` (schema + log). Chạy thật trên Raspberry Pi như
   **systemd service tự khởi động**. Repo public: github.com/bnqtoan/smart-greenhouse-iot ·
   hub site: bnqtoan.github.io/smart-greenhouse-iot.
10. **Kết quả & Kết luận** — chạy thật trên phần cứng: ảnh + dashboard Live + bảng đối chiếu rubric (mức 9–10).
    Đã làm: giám sát + tự động + **chống cháy** + **cảnh báo Telegram**. Mở rộng: thêm cảm biến, cloud, app mobile.

## Bảng đối chiếu rubric (đưa vào slide 10)
| Tiêu chí | Mức 9–10 | Đã đạt |
|---|---|---|
| Arduino | ≥2 cảm biến + LCD + actuator | DHT22+LDR + LCD1602 + LED+Servo+Buzzer ✅ |
| **Giao tiếp** | **Bluetooth (backup Serial)** | **HC-05 Bluetooth /dev/rfcomm0 + USB auto-backup ✅ (mức cao nhất)** |
| Raspberry Pi | Flask dashboard + điều khiển | ✅ |
| Lưu dữ liệu | SQLite | ✅ |
| Dashboard | hiện tại + lịch sử + chart | ✅ (dark glassmorphism + Chart.js) |
| Điều khiển GUI | bắt buộc | LED/Vent/Mode/Ngưỡng ✅ |
| Bonus sáng tạo | UI đẹp + chart + auto/manual | + **Fire protection** (buzzer+servo tự động) + **Telegram remote alarm** + systemd deploy + GitHub Pages ✅ |

> Điểm mạnh: cột "Giao tiếp" đạt **đúng mức cao nhất = Bluetooth có backup Serial** (truyền không dây thật,
> rớt BT vẫn online qua USB). Bonus vượt scope: tự bảo vệ chống cháy + cảnh báo từ xa qua Telegram.

## Video demo (3–7 phút) cần quay
phần cứng → cảm biến đổi giá trị (che LDR, hà hơi vào DHT) → JSON truyền sang Pi →
**show Bluetooth hoạt động: rút cáp USB, dashboard vẫn "Live · Bluetooth"** →
dashboard Live + chart → bấm điều khiển LED/cửa → đổi Auto/Manual →
**trigger cháy/quá nhiệt → buzzer hú + servo tự mở cửa + banner đỏ + thông báo Telegram hiện trên điện thoại** →
mở file SQLite cho thấy log.
