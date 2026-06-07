# 📶 Playbook: Kết nối Bluetooth giữa Arduino ↔ Raspberry Pi (HC-05)

Hướng dẫn đơn giản, đúng những bước nhóm mình đã làm. Mục tiêu: Arduino gửi dữ liệu
**không dây** sang Pi qua module **HC-05**, USB chỉ làm dự phòng.

> Ý tưởng chính: HC-05 là "cái loa radio" của Arduino.
> - **Arduino ↔ HC-05**: nối bằng dây (vài sợi).
> - **HC-05 ))) Pi**: không dây (Bluetooth thật).

---

## 1. SETUP — Nối HC-05 vào Arduino (4 dây)

| HC-05 | → Arduino | Ghi chú |
|---|---|---|
| VCC | 5V | nguồn |
| GND | GND | mát |
| TXD | **D10** | HC-05 gửi dữ liệu → Arduino |
| RXD | **D11** | Arduino gửi → HC-05 (⚠️ xem dưới) |

**⚠️ Chân RXD (D11→HC-05 RXD):** Arduino xuất 5V nhưng HC-05 RXD chỉ chịu 3.3V.
Dùng cầu chia áp: `D11 ──[1kΩ]──┬── HC-05 RXD ; ┴──[2kΩ]── GND`.
→ Để test nhanh (chỉ cần Arduino GỬI dữ liệu), có thể tạm bỏ dây RXD, chỉ nối VCC/GND/TXD→D10.

**Vì sao D10/D11 mà không phải D0/D1?** D0/D1 là cổng USB dùng để nạp code + làm
backup. Dùng D10/D11 (SoftwareSerial) thì **cả USB lẫn Bluetooth chạy song song**.

Đèn HC-05 **nháy nhanh** = đã có điện, đang chờ ghép đôi. ✅

---

## 2. CODE — Arduino gửi dữ liệu ra cả USB + Bluetooth

File: [`arduino/greenhouse/greenhouse.ino`](../arduino/greenhouse/greenhouse.ino)

Phần cốt lõi:
```cpp
#include <SoftwareSerial.h>
#define USE_BLUETOOTH
SoftwareSerial bt(10, 11);   // (RX=D10, TX=D11)

void setup() {
  Serial.begin(9600);        // USB
  bt.begin(9600);            // Bluetooth (HC-05 mặc định 9600)
}

void report() {              // gửi JSON ra CẢ HAI
  String j = "{\"temp\":...}";
  Serial.println(j);         // qua USB
  bt.println(j);             // qua Bluetooth
}

void loop() {                // nhận lệnh từ CẢ HAI
  while (Serial.available()) handleCommand(Serial.readStringUntil('\n'));
  while (bt.available())     handleCommand(bt.readStringUntil('\n'));
}
```

### ⚠️ BẪY QUAN TRỌNG — xung đột timer (nhóm mình mất nhiều giờ ở đây!)
Arduino Uno có ít timer, 3 thứ tranh nhau:
| Thứ | Dùng timer | Làm hỏng |
|---|---|---|
| Thư viện `Servo` | Timer1 | → chết **Bluetooth** (SoftwareSerial) |
| `ServoTimer2` | Timer2 | → chết **DHT22** (đọc sai, ra 0.0) |
| **Bit-bang servo (chọn cái này)** | KHÔNG dùng timer | → không hỏng gì ✅ |

→ Giải pháp: **không dùng thư viện servo**, tự tạo xung cho servo bằng `digitalWrite`:
```cpp
void setVent(bool open) {
  int us = open ? 2000 : 1000;          // 2000us=mở, 1000us=đóng
  for (int i = 0; i < 50; i++) {        // ~1 giây xung
    noInterrupts();
    digitalWrite(SERVO_PIN, HIGH);
    delayMicroseconds(us);
    digitalWrite(SERVO_PIN, LOW);
    interrupts();
    delay(20);                          // ~50Hz
  }
}
```
Cách này servo + DHT22 + Bluetooth chạy cùng lúc, không xung đột.

---

## 3. MOUNT — Ghép đôi Pi với HC-05 (không dây, làm trên Pi)

Chạy trên Raspberry Pi (qua SSH hoặc terminal):

```bash
# 1. Quét tìm module (xem tên + địa chỉ MAC)
bluetoothctl --timeout 12 scan on | grep -i arduino
# ví dụ thấy:  98:D3:C1:FD:5C:B7 NHOM2_ARDUINO

# 2. Ghép đôi (PIN HC-05 mặc định 1234)
bluetoothctl
  > trust 98:D3:C1:FD:5C:B7
  > pair  98:D3:C1:FD:5C:B7      # nhập PIN: 1234
  > quit

# 3. Gắn HC-05 vào cổng serial /dev/rfcomm0
sudo rfcomm bind 0 98:D3:C1:FD:5C:B7 1
ls /dev/rfcomm0                  # phải thấy file này

# 4. Đọc thử dữ liệu qua Bluetooth
python3 -c "import serial;s=serial.Serial('/dev/rfcomm0',9600,timeout=3);print(s.readline())"
# thấy JSON {"temp":...} = THÀNH CÔNG 🎉
```

> Thay `98:D3:C1:FD:5C:B7` bằng MAC module CỦA BẠN (bước 1).

### App tự ưu tiên Bluetooth, USB dự phòng
File [`rpi/app.py`](../rpi/app.py) thử lần lượt — cái nào mở được thì dùng:
```python
SERIAL_PORTS = ["/dev/rfcomm0", "/dev/ttyACM0", "/dev/ttyUSB0"]
# rfcomm0 = Bluetooth (ưu tiên), ttyACM0 = USB (backup)
```
→ Có Bluetooth thì chạy không dây; rớt Bluetooth thì tự nhảy về USB.

---

## 4. LƯU Ý KHI DEMO / SAU KHI REBOOT

`rfcomm bind` **mất sau khi reboot Pi**. Trước khi demo, nếu Pi vừa khởi động lại:
```bash
sudo rfcomm bind 0 <MAC-CỦA-BẠN> 1
sudo systemctl restart greenhouse     # nếu chạy bằng service
```

Lỗi thường gặp:
- **"Chưa kết nối Arduino"** dù đã cắm USB → có thể `rfcomm0` còn bind nhưng HC-05 tắt;
  gỡ bằng `sudo rfcomm release 0` rồi app sẽ tự dùng USB.
- **HC-05 không thấy khi quét** → kiểm tra đèn HC-05 có nháy nhanh không (chưa có điện).
- **Ghép đôi báo PIN sai** → thử PIN `0000` thay vì `1234`.

---

## Tóm tắt 1 dòng
`Arduino --4 dây--> HC-05 ))) Bluetooth ))) Pi (/dev/rfcomm0)` — code gửi JSON ra cả
USB + BT, Pi ưu tiên BT và tự backup USB. Tránh thư viện Servo (dùng bit-bang) để
khỏi xung đột timer với Bluetooth/DHT22.
