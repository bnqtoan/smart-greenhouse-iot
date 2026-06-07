# Smart Greenhouse — IoT Final (IAD591)

Hệ thống nhà kính thông minh 3 tầng: **Arduino (cảm biến/điều khiển) → cáp USB → Raspberry Pi (Flask + SQLite) → Dashboard**.

## Cấu trúc
```
final/
├── arduino/greenhouse/greenhouse.ino   # nạp lên Arduino Uno
├── rpi/
│   ├── app.py                          # chạy trên Pi: python3 app.py
│   ├── requirements.txt                # flask, pyserial
│   ├── templates/index.html            # dashboard dark glassmorphism
│   └── greenhouse.db                   # SQLite tự tạo
└── docs/
    ├── WIRING.md                       # sơ đồ đấu nối + bảng pin
    ├── BUILD_CHECKLIST.md              # thứ tự lắp & test (2 lớp) ⬅ ĐỌC TRƯỚC
    └── SLIDES_OUTLINE.md               # dàn ý slide + đối chiếu rubric
```

## Chạy nhanh
1. Arduino IDE: cài *DHT sensor library*, *LiquidCrystal_I2C* → nạp `greenhouse.ino`.
2. Cắm Arduino vào **USB của Pi**.
3. Trên Pi: `cd rpi && pip3 install -r requirements.txt && python3 app.py`
4. Mở `http://<ip-pi>:5000`.

## Điểm mạnh chống lỗi lab
- Nối Arduino↔Pi bằng **cáp USB** (không TX/RX, không hạ áp).
- Servo & LCD là **tuỳ chọn** (`#define` trong .ino) — tháo ra không ảnh hưởng phần còn lại.
- Không có Arduino → dashboard tự chạy **chế độ Simulated**, demo không bao giờ sập.
