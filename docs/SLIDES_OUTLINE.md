# SLIDE OUTLINE (8–10 slide) — Smart Greenhouse

1. **Bìa** — Smart Greenhouse · IAD591 · tên nhóm + thành viên (MSSV).
2. **Giới thiệu hệ thống** — Bài toán: giám sát & tự động hoá nhà kính mini.
   Mục tiêu: đo nhiệt/ẩm/sáng, tự bật đèn & mở cửa thông gió, dashboard điều khiển từ xa.
3. **Kiến trúc 3 tầng** — sơ đồ: Arduino (Device) → USB Serial → Pi (Gateway) → Flask+SQLite (App).
   Nhấn: nối USB trực tiếp ⇒ ổn định, không hạ áp.
4. **Sơ đồ phần cứng / đấu nối** — ảnh breadboard + bảng pin (DHT22 D2, LDR A0, LED D7, Servo D9, LCD I2C).
5. **Luồng dữ liệu** — Arduino đọc cảm biến → JSON 1s/lần → Pi parse → SQLite → API → Dashboard;
   lệnh điều khiển web → Pi → Arduino (LED/VENT/MODE/threshold).
6. **Logic tự động** — đèn bật khi tối (light < ngưỡng); cửa mở khi nóng (temp > ngưỡng);
   Auto/Manual mode.
7. **Dashboard (ảnh chụp)** — metric cards, chart realtime, công tắc điều khiển, đặt ngưỡng.
   Nhấn các tiêu chí rubric: hiện tại + lịch sử + chart + điều khiển.
8. **Lưu trữ dữ liệu** — SQLite `readings`, ảnh schema + vài dòng log.
9. **Kết quả** — chạy thật: ảnh phần cứng + dashboard Live; bảng đối chiếu rubric (đã đạt mức 9–10).
10. **Kết luận** — đã làm được / hướng mở rộng (Bluetooth, nhiều cảm biến, cảnh báo).

## Bảng đối chiếu rubric (đưa vào slide 9)
| Tiêu chí | Mức 9–10 | Đã đạt |
|---|---|---|
| Arduino | ≥2 cảm biến + LCD + actuator | DHT22+LDR + LCD + LED+Servo ✅ |
| Giao tiếp | (Serial ổn định qua USB) | USB Serial /dev/ttyACM0 ✅ |
| Raspberry Pi | Flask dashboard + điều khiển | ✅ |
| Lưu dữ liệu | SQLite | ✅ |
| Dashboard | hiện tại + lịch sử + chart | ✅ |
| Điều khiển GUI | bắt buộc | LED/Vent/Mode/Ngưỡng ✅ |
| Bonus | UI đẹp + chart + auto/manual sáng tạo | +0.75 ✅ |

> Lưu ý chấm điểm: rubric mức 9–10 cột "Giao tiếp" ghi Bluetooth. Ta chọn USB Serial ổn định
> để tránh rủi ro lab; bù lại tối đa hoá Bonus phần mềm. Nếu giám khảo yêu cầu BT, có HC-05 dự phòng
> chỉ là đổi cổng serial (cùng code).

## Video demo (3–7 phút) cần quay
phần cứng → cảm biến đổi giá trị (che LDR, hà hơi vào DHT) → JSON truyền sang Pi →
dashboard Live + chart → bấm điều khiển LED/cửa → đổi Auto/Manual → mở file SQLite cho thấy log.
