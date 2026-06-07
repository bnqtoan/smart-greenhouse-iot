# Smart Greenhouse — IoT Final (IAD591)

## 👉 TRANG HƯỚNG DẪN CHO NHÓM (xem cái này trước)
### https://bnqtoan.github.io/smart-greenhouse-iot/
Trang tổng hợp tất cả: tổng quan, kiến trúc, sơ đồ đấu nối tương tác, các bước lắp ráp, cách chạy, link mọi tài liệu. Mở trên điện thoại/laptop đều được.

---

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
    ├── BUILD_CHECKLIST.md              # thứ tự lắp & test ⬅ ĐỌC TRƯỚC
    ├── BLUETOOTH_PLAYBOOK.md           # 📶 kết nối Bluetooth Arduino↔Pi (HC-05)
    └── SLIDES_OUTLINE.md               # dàn ý slide + đối chiếu rubric
```

## 📶 Kết nối Bluetooth (HC-05)
Hướng dẫn đầy đủ + code: [`docs/BLUETOOTH_PLAYBOOK.md`](docs/BLUETOOTH_PLAYBOOK.md)

## 📺 Xem cách đấu nối (visual)
- **Sơ đồ breadboard chính xác** (đấu theo hình này): `docs/wiring-breadboard.svg`
  *(tạo bằng code `docs/gen_breadboard.py` — chính xác từng chân, không phải ảnh AI)*
- **Trang tương tác** (bấm linh kiện → highlight dây): `docs/wiring.html`
- **Sơ đồ khối**: `docs/wiring.svg`

## Chạy nhanh
1. Arduino IDE: cài *DHT sensor library*, *LiquidCrystal_I2C* → nạp `greenhouse.ino`.
2. Cắm Arduino vào **USB của Pi**.
3. Trên Pi: `cd rpi && pip3 install -r requirements.txt && python3 app.py`
4. Mở `http://<ip-pi>:5000`.

## Điểm mạnh chống lỗi lab
- Nối Arduino↔Pi bằng **cáp USB** (không TX/RX, không hạ áp).
- Servo & LCD là **tuỳ chọn** (`#define` trong .ino) — tháo ra không ảnh hưởng phần còn lại.
- Không có Arduino → dashboard tự chạy **chế độ Simulated**, demo không bao giờ sập.
