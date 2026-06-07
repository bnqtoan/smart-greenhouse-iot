# Wokwi — sơ đồ mạch SỐNG (mô phỏng được, sửa được)

Đây là sơ đồ mạch **thật, khai báo bằng code** (`diagram.json`) — không phải ảnh AI.
Mở trên Wokwi để **xem, sửa, và MÔ PHỎNG chạy thật** trước khi đụng phần cứng.

## Cách mở (3 cách)

### Cách 1 — nhanh nhất: dán lên wokwi.com
1. Vào https://wokwi.com → **New Project** → chọn **Arduino Uno**.
2. Mở tab **diagram.json**, xoá hết, dán nội dung file `diagram.json` ở đây vào.
3. Mở tab **sketch.ino**, dán nội dung `sketch.ino` vào.
4. Bấm ▶ **Start** → mạch chạy mô phỏng. Kéo slider trên DHT22 / quang trở để xem LED + servo phản ứng.

### Cách 2 — Wokwi cho VS Code (mô phỏng ngay trong editor)
1. Cài extension **"Wokwi Simulator"** trong VS Code.
2. Mở folder `wokwi/` này → bấm **F1 → Wokwi: Start Simulator**.

### Cách 3 — import từ GitHub
Trên wokwi.com → **Import** → dán link repo: `github.com/bnqtoan/smart-greenhouse-iot` (thư mục `wokwi/`).

## File
| File | Vai trò |
|---|---|
| `diagram.json` | **Nguồn chân lý** — khai báo linh kiện + dây nối (8 part, 18 dây). Sửa file này = sửa mạch. |
| `sketch.ino` | Code mô phỏng (bản rút gọn của greenhouse.ino, chỉ logic local). |
| `wokwi.toml` | Cấu hình project Wokwi. |
| `libraries.txt` | Thư viện cần (DHT, Servo, LiquidCrystal_I2C). |

## Bản đồ chân (khớp 100% với phần cứng thật)
```
DHT22 DATA → D2     LDR AO → A0      LED+220Ω → D7
Servo PWM → D9      LCD I2C → A4(SDA)/A5(SCL)
Nguồn 5V/GND qua thanh rail breadboard
```

> ⚠️ Wokwi dùng **module quang trở** (có sẵn chân AO). Phần cứng thật của nhóm
> dùng **LDR + trở 10kΩ chia áp** — cùng đọc trên A0, logic y hệt.
>
> Bản build thật (có gửi serial JSON sang Pi): xem `../arduino/greenhouse/greenhouse.ino`.
