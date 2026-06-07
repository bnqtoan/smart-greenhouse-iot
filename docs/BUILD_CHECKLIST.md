# BUILD CHECKLIST — thứ tự lắp & test (2 lớp)

> 📺 **XEM SƠ ĐỒ ĐẤU NỐI TRƯỚC KHI LẮP:**
> - Trang hướng dẫn đầy đủ: **https://bnqtoan.github.io/smart-greenhouse-iot/**
> - Sơ đồ breadboard chính xác từng chân (có khoanh vùng Layer 1 / Layer 2): [`wiring-breadboard.svg`](./wiring-breadboard.svg)
> - Sơ đồ tương tác (bấm linh kiện → highlight dây): [`wiring.html`](./wiring.html)

> Quy tắc vàng: **test từng phần ngay sau khi lắp**. Đừng lắp hết rồi mới bật.
> Mỗi bước phải PASS mới qua bước sau. Layer 1 xong = đã chắc 8 điểm.

## 📌 Bản đồ chân (nguồn chân lý — khớp với code & sơ đồ)
| Linh kiện | Chân | Layer |
|---|---|---|
| DHT22 DATA | **D2** | 🟢 Layer 1 |
| LDR (chia áp 10kΩ) | **A0** | 🟢 Layer 1 |
| LED + 220Ω | **D7** | 🟢 Layer 1 |
| Servo SG90 | **D9** | 🟡 Layer 2 |
| LCD1602 I2C (0x27) | **A4=SDA, A5=SCL** | 🟡 Layer 2 |
| Buzzer (còi báo cháy) | **D8** (trên Arduino) | 🔴 Layer 3 |
| 4-digit 7-seg + 74HC595 | **trên RASPBERRY PI** GPIO BCM 17/27/22 (3.3V) | 🔴 Layer 3 |
| Nguồn | 5V / GND | — |
| Arduino → Pi | **CÁP USB** (/dev/ttyACM0) | — |

## CHUẨN BỊ (10 phút)
- [ ] Cắm Arduino vào **laptop** (lắp/nạp code dễ hơn), sẽ chuyển sang Pi ở bước cuối.
- [ ] Cài thư viện Arduino IDE: **DHT sensor library** (Adafruit), **LiquidCrystal_I2C**.
- [ ] Trên Pi: `pip3 install flask pyserial`.

## ===== LAYER 1 — LÕI AN TOÀN (mục tiêu: ~8 điểm) =====

### B1. DHT22 (5 phút)
- [ ] Lắp DHT22: VCC→5V, DATA→D2, GND→GND.
- [ ] Nạp `greenhouse.ino`, mở Serial Monitor (9600).
- [ ] PASS khi thấy JSON có `temp`, `hum` ≠ 0.

### B2. LDR (5 phút)
- [ ] Lắp chia áp: 5V—LDR—A0—R10k—GND.
- [ ] Lấy tay che/rọi đèn → `light` trong JSON thay đổi rõ.
- [ ] Ghi lại giá trị tối/sáng → đặt ngưỡng (mặc định 400).

### B3. LED grow-light (3 phút)
- [ ] LED + 220Ω: chân dài→D7, chân ngắn→GND.
- [ ] Gõ `LED:1` ↵ trong Serial Monitor → LED sáng. `LED:0` → tắt.
- [ ] PASS khi điều khiển được + che LDR (chế độ auto) thì LED tự bật.

### B4. Nối Arduino → Pi bằng CÁP USB (5 phút)  ⬅ điểm mấu chốt
- [ ] Rút Arduino khỏi laptop, cắm vào **cổng USB của Pi**.
- [ ] Trên Pi: `ls /dev/ttyACM*` → thấy `/dev/ttyACM0`.
- [ ] Nếu khác (ttyACM1/ttyUSB0) → sửa `SERIAL_PORT` trong `app.py`.

### B5. Flask dashboard (5 phút)
- [ ] `cd rpi && python3 app.py`
- [ ] Mở `http://<ip-pi>:5000` trên trình duyệt.
- [ ] PASS khi: pill hiện **"Live · Arduino"** (xanh), số liệu chạy, chart vẽ,
      bấm MANUAL rồi gạt công tắc Đèn → LED thật sáng/tắt.

✅ **ĐẾN ĐÂY ĐÃ ĐỦ: 2 cảm biến + actuator + Flask + SQLite + chart + điều khiển GUI.**

## ===== LAYER 2 — TĂNG ĐIỂM (làm nếu còn thời gian, mỗi phần độc lập) =====

### B6. Servo cửa thông gió (+ điểm actuator/auto)  ~10 phút
- [ ] Servo: Đỏ→5V, Nâu→GND, Cam→D9. (đảm bảo `#define USE_SERVO` còn bật)
- [ ] Gõ `VENT:1`/`VENT:0` → servo quay 90°/0°.
- [ ] Auto: nhiệt > ngưỡng → cửa tự mở.
- [ ] ⚠️ Nếu servo giật/reset Arduino → cấp nguồn riêng cho servo HOẶC bỏ `#define USE_SERVO` (demo vẫn chạy).

### B7. LCD1602 I2C (+ dòng rubric LCD)  ~10 phút
- [ ] I2C: VCC→5V, GND→GND, SDA→A4, SCL→A5. (`#define USE_LCD` bật)
- [ ] Hiện T/H + mode trên LCD.
- [ ] ⚠️ Màn trắng/không chữ → vặn biến trở contrast sau LCD; vẫn trắng → đổi `0x27`→`0x3F`; vẫn lỗi → bỏ `#define USE_LCD`.

### B8. Bonus phần mềm (gần như miễn phí điểm)
- [ ] Chế độ Auto/Manual đã có sẵn trên dashboard → quay demo cảnh chuyển mode.
- [ ] Chỉnh ngưỡng trên web → quay cảnh đổi ngưỡng làm đèn/cửa đổi trạng thái.

## ===== LAYER 3 — TÍNH NĂNG "ĂN ĐIỂM" (chống cháy + LED 4 digit) =====

### B9. Buzzer + cảnh báo cháy/quá nhiệt (trên Arduino)  ~5 phút
- [ ] Buzzer (loại active): chân **+ → D8**, chân **− → GND**.
- [ ] Logic đã có sẵn trong code: `temp ≥ 50°C` → buzzer kêu + servo tự mở cửa + cờ `fire` gửi lên Pi.
- [ ] Test: hơ bật lửa/máy sấy gần DHT22 → nhiệt tăng → buzzer kêu + dashboard hiện **banner đỏ "CẢNH BÁO CHÁY"**.
- [ ] Đổi ngưỡng cháy: gõ `TH_FIRE:45` trong Serial Monitor (mặc định 50).
- [ ] 💡 Câu chuyện sản phẩm: "hệ thống không chỉ giám sát mà còn **bảo vệ tài sản** khỏi cháy/quá nhiệt".

### B10. LED 4 digit trên Raspberry Pi (rubric: cột Pi mức 9–10)  ~15 phút
> ⚠️ Phần này lắp trên **breadboard riêng nối thẳng vào GPIO của Raspberry Pi** (không qua Arduino).
> Cấp nguồn 74HC595 bằng **3.3V của Pi** — KHÔNG cần hạ áp.
- [ ] 74HC595: VCC(16)→3.3V, GND(8)→GND, MR(10)→3.3V, OE(13)→GND.
- [ ] DS(14)→**GPIO17**, STCP(12)→**GPIO27**, SHCP(11)→**GPIO22** (đánh số BCM).
- [ ] Q0..Q7 → 8 thanh LED (a..g, dp) qua trở 220–330Ω.
- [ ] 4 chân chung của 4 digit → **GPIO23, 24, 25, 12**.
- [ ] Trên Pi: `pip3 install RPi.GPIO` rồi chạy lại `app.py`.
- [ ] PASS: LED 4 digit hiện nhiệt độ (vd `27.5`); khi cháy → nhấp nháy **"FirE"**.
- [ ] ⚠️ Nếu không có RPi.GPIO / chưa lắp → app vẫn chạy bình thường, chỉ là không có LED.

## DỰ PHÒNG KHI DEMO (đừng hoảng)
- Arduino chưa cắm? Dashboard hiện **"Chưa kết nối Arduino"** (không có dữ liệu giả), tự nối lại khi cắm Arduino.
- Sai cổng serial → sửa `SERIAL_PORT` trong `app.py`.
- Module hỏng (servo/LCD/buzzer/4-digit) → tháo ra hoặc bỏ `#define`/không cài RPi.GPIO; phần còn lại vẫn chạy.
