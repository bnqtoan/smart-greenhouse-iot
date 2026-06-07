# BUILD CHECKLIST — thứ tự lắp & test (2 lớp)

> Quy tắc vàng: **test từng phần ngay sau khi lắp**. Đừng lắp hết rồi mới bật.
> Mỗi bước phải PASS mới qua bước sau. Layer 1 xong = đã chắc 8 điểm.

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

## DỰ PHÒNG KHI DEMO (đừng hoảng)
- Arduino không nhận? Dashboard tự chuyển **"Demo · Simulated"** → vẫn trình bày được chart + điều khiển, không sập.
- Sai cổng serial → sửa `SERIAL_PORT`.
- Một module hỏng → tháo `#define` tương ứng, nạp lại, phần còn lại vẫn chạy.
