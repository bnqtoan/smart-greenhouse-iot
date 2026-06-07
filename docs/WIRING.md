# Smart Greenhouse — Wiring (an toàn, ít dây)

## Nguyên tắc giảm rủi ro phần cứng
1. **Arduino nối Pi bằng cáp USB** (Arduino USB → cổng USB của Pi). KHÔNG dùng dây TX/RX.
   → Pi đọc tại `/dev/ttyACM0`. Loại bỏ hoàn toàn lỗi Arduino↔Pi trước đây + không cần hạ áp.
2. Mọi cảm biến/actuator nằm **hết trên Arduino** (Arduino có chân analog cho LDR; Pi thì không).
3. Servo + LCD là **tuỳ chọn** (Layer 2). Hỏng/không gắn → code vẫn chạy, demo không sập.

## Sơ đồ kết nối

```mermaid
flowchart LR
    subgraph DEV["TẦNG THIẾT BỊ — Arduino Uno"]
        DHT["DHT22<br/>VCC·DATA·GND"]
        LDR["LDR + R10k<br/>(chia áp → A0)"]
        LED["LED + R220Ω<br/>→ D7"]
        SERVO["Servo SG90<br/>(tuỳ chọn → D9)"]
        LCD["LCD1602 I2C<br/>(tuỳ chọn → SDA/SCL)"]
    end
    DHT -->|D2| ARD[Arduino Uno]
    LDR -->|A0| ARD
    ARD -->|D7| LED
    ARD -->|D9 PWM| SERVO
    ARD -->|A4 SDA / A5 SCL| LCD
    ARD ==>|CÁP USB| PI["TẦNG GATEWAY<br/>Raspberry Pi 3B+<br/>/dev/ttyACM0"]
    PI --> FLASK["TẦNG ỨNG DỤNG<br/>Flask + SQLite<br/>Dashboard + Chart"]
```

## Bảng chân (pin map)

| Linh kiện | Chân Arduino | Ghi chú |
|---|---|---|
| DHT22 — DATA | D2 | VCC→5V, GND→GND. (module DHT22 thường có trở kéo sẵn) |
| LDR | A0 | Chia áp: 5V — LDR — A0 — R10kΩ — GND |
| LED grow-light | D7 | Nối tiếp trở 220Ω, chân dài (+) về D7, chân ngắn về GND |
| Servo SG90 *(L2)* | D9 (PWM) | Đỏ→5V, Nâu→GND, Cam→D9 |
| LCD1602 I2C *(L2)* | A4=SDA, A5=SCL | VCC→5V, GND→GND, địa chỉ 0x27 (nếu trắng màn → đổi 0x3F) |
| Buzzer báo cháy *(L3)* | D8 | Active buzzer: + → D8, − → GND. Kêu khi `temp ≥ 50°C` |
| Arduino → Pi | **Cáp USB** | KHÔNG dùng TX/RX. Pi đọc /dev/ttyACM0 |

### LED 4 digit — lắp trên RASPBERRY PI (Layer 3, không qua Arduino)
Dùng 74HC595 + 4-digit 7-seg trên breadboard riêng, cấp **3.3V từ Pi** (không hạ áp).

| 74HC595 | Pi (BCM) | Ghi chú |
|---|---|---|
| DS (14) | GPIO24 | data (SDI) |
| STCP (12) | GPIO23 | latch (RCLK) |
| SHCP (11) | GPIO18 | clock (SRCLK) |
| VCC (16), MR (10) | 3.3V | |
| GND (8), OE (13) | GND | OE→GND để bật output |
| Q0..Q7 | a,b,c,d,e,f,g,dp | qua trở 220–330Ω |
| 4 chân digit chung | GPIO10, GPIO22, GPIO27, GPIO17 | digit 0→3 (HIGH = bật digit) |

> Theo đúng sơ đồ **SunFounder Raphael-kit "1.1.5 4-Digit 7-Segment"**. LED loại
> **common-anode** (mã đoạn đảo). Code `sevenseg.py` đã set sẵn đúng các chân này.

Pi tự đẩy nhiệt độ ra LED 4 digit (hiện `27.5`); khi cháy nhấp nháy `FirE`.
→ Đúng yêu cầu rubric cột **Raspberry Pi mức 9–10 ("LED 4 digit")**: chính Pi điều khiển hiển thị.

## Mạch chia áp LDR (chi tiết)
```
5V ──[ LDR ]──┬── A0
              │
            [ R 10kΩ ]
              │
             GND
```
Trời tối → LDR điện trở cao → điện áp A0 thấp → giá trị ADC thấp → bật đèn.
(Ngưỡng mặc định 400; chỉnh trên dashboard cho khớp ánh sáng phòng lab.)
