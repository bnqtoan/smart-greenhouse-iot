#!/usr/bin/env python3
"""
Generate a pin-accurate, Fritzing-style breadboard wiring SVG for the
Smart Greenhouse project — diagram as code, reproducible & committable.

Every wire endpoint is computed from the actual header/breadboard hole
coordinates, so the connections are engineering-correct (not decorative).

Pin map (matches greenhouse.ino):
  DHT22  DATA -> D2     VCC -> 5V    GND -> GND
  LDR divider middle -> A0   (5V - LDR - A0 - 10k - GND)
  LED   anode via 220R -> D7   cathode -> GND
  Servo signal -> D9   V+ -> 5V   GND -> GND
  LCD   SDA -> A4   SCL -> A5   VCC -> 5V   GND -> GND
  Arduino <-> Pi : USB cable (drawn as a labelled USB plug, no signal wires)

Run:  python3 gen_breadboard.py  ->  writes wiring-breadboard.svg
"""

W, H = 1180, 880
parts = []
def add(s): parts.append(s)

# ---------- colors ----------
RED="#e23b3b"; BLK="#222"; YEL="#f4c430"; ORN="#f08000"; BLU="#4aa3ff"; GRN="#2faa55"
WIRE_W = 4

def wire(x1,y1,x2,y2,color,mid=None):
    """smooth wire with a white halo underneath so crossings read clearly (Fritzing style)."""
    if mid is None:
        cx = (x1+x2)/2
        d = f'M{x1},{y1} C{cx},{y1} {cx},{y2} {x2},{y2}'
    else:
        mx,my = mid
        d = f'M{x1},{y1} Q{mx},{my} {x2},{y2}'
    # halo
    add(f'<path d="{d}" stroke="#fbfcfe" stroke-width="{WIRE_W+3}" fill="none" stroke-linecap="round"/>')
    # wire
    add(f'<path d="{d}" stroke="{color}" stroke-width="{WIRE_W}" fill="none" stroke-linecap="round"/>')

def hole(x,y,r=3.0,fill="#3a3a3a"):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>')

# =========================================================
#  CANVAS
# =========================================================
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#fbfcfe"/>')
add(f'<text x="28" y="40" font-size="24" font-weight="700" fill="#0f172a">🌱 Smart Greenhouse — Sơ đồ đấu nối (chính xác từng chân)</text>')
add(f'<text x="28" y="64" font-size="13" fill="#475569">Arduino nối Raspberry Pi bằng CÁP USB. Mọi cảm biến/actuator gắn trên Arduino.</text>')
# legend chips
lx=28; ly=82
for col,lbl in [(RED,"5V"),(BLK,"GND"),(YEL,"tín hiệu"),(ORN,"PWM servo"),(BLU,"I2C")]:
    add(f'<line x1="{lx}" y1="{ly}" x2="{lx+24}" y2="{ly}" stroke="{col}" stroke-width="4" stroke-linecap="round"/>')
    add(f'<text x="{lx+30}" y="{ly+4}" font-size="12" fill="#334155">{lbl}</text>')
    lx += 40 + len(lbl)*7 + 30

# =========================================================
#  LAYER ZONES (drawn first, behind everything)
# =========================================================
L1="#16a34a"; L2="#d97706"
def zone(x,y,w,h,color,fill):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" '
        f'stroke="{color}" stroke-width="2.5" stroke-dasharray="10 6"/>')
def tag(x,y,color,text):
    w=len(text)*7+18
    add(f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{color}"/>')
    add(f'<text x="{x+w/2}" y="{y+15}" text-anchor="middle" font-size="11" font-weight="800" fill="#fff">{text}</text>')

# Layer 1 zone: wraps DHT22 + LDR breadboard + LED breadboard (top strip)
zone(452, 78, 666, 152, L1, "#16a34a12")
tag(452, 56, L1, "🟢 LAYER 1 — LÕI AN TOÀN (DHT22 + LDR + LED)")

# Layer 2 zone A: Servo (right)
zone(958, 332, 200, 120, L2, "#d9770612")
tag(958, 310, L2, "🟡 LAYER 2 — TĂNG ĐIỂM (tuỳ chọn)")

# Layer 2 zone B: LCD (bottom)
zone(452, 540, 330, 158, L2, "#d9770612")
tag(452, 518, L2, "🟡 LAYER 2 — TĂNG ĐIỂM (tuỳ chọn)")

# =========================================================
#  ARDUINO UNO  (left)
# =========================================================
AX, AY, AW, AH = 60, 300, 360, 240
add(f'<rect x="{AX}" y="{AY}" width="{AW}" height="{AH}" rx="14" fill="#1a8a93" stroke="#0f6e75" stroke-width="2"/>')
add(f'<text x="{AX+AW/2}" y="{AY+AH/2}" text-anchor="middle" font-size="18" font-weight="800" fill="#ffffff" opacity="0.85">ARDUINO UNO</text>')
add(f'<text x="{AX+AW/2}" y="{AY+AH/2+20}" text-anchor="middle" font-size="11" fill="#d6f5f8">R3</text>')
# chip
add(f'<rect x="{AX+150}" y="{AY+150}" width="120" height="34" rx="3" fill="#222"/>')
# USB plug (to Pi)
add(f'<rect x="{AX-30}" y="{AY+30}" width="34" height="44" rx="4" fill="#c8cdd4" stroke="#9aa1ab"/>')
add(f'<rect x="{AX-26}" y="{AY+38}" width="26" height="28" rx="2" fill="#8a9099"/>')

# --- TOP digital header (pins 13..0) ---
# We place named pins we use: D7, D9, D2 along the top, plus power along bottom-left.
top_y = AY + 14
def header_pin(x,y,label,side="top"):
    add(f'<rect x="{x-9}" y="{y-9}" width="18" height="18" rx="3" fill="#111"/>')
    add(f'<circle cx="{x}" cy="{y}" r="4.5" fill="#3a3a3a"/>')
    if side=="top":
        add(f'<text x="{x}" y="{y-13}" text-anchor="middle" font-size="11" font-weight="700" fill="#063">{label}</text>')
    else:
        add(f'<text x="{x}" y="{y+22}" text-anchor="middle" font-size="11" font-weight="700" fill="#063">{label}</text>')

# digital pins along top edge
D7  = (AX+230, top_y); header_pin(*D7,"D7")
D9  = (AX+270, top_y); header_pin(*D9,"D9~")
D8  = (AX+310, top_y); header_pin(*D8,"D8")
D2  = (AX+150, top_y); header_pin(*D2,"D2")
# power+analog along bottom edge
bot_y = AY+AH-14
P5V  = (AX+70,  bot_y); header_pin(*P5V,"5V","bot")
GND1 = (AX+110, bot_y); header_pin(*GND1,"GND","bot")
A0   = (AX+180, bot_y); header_pin(*A0,"A0","bot")
A4   = (AX+250, bot_y); header_pin(*A4,"A4","bot")
A5   = (AX+290, bot_y); header_pin(*A5,"A5","bot")

# =========================================================
#  POWER RAILS (a small power distribution for 5V/GND fanout)
# =========================================================
# Use a mini breadboard power rail so multiple comps share 5V & GND cleanly.
RAILX, RAILY = 470, 250
add(f'<rect x="{RAILX}" y="{RAILY}" width="640" height="40" rx="6" fill="#f4f5f7" stroke="#d6dae0"/>')
add(f'<line x1="{RAILX+10}" y1="{RAILY+12}" x2="{RAILX+630}" y2="{RAILY+12}" stroke="{RED}" stroke-width="2"/>')
add(f'<line x1="{RAILX+10}" y1="{RAILY+28}" x2="{RAILX+630}" y2="{RAILY+28}" stroke="{BLK}" stroke-width="2"/>')
add(f'<text x="{RAILX-6}" y="{RAILY+16}" text-anchor="end" font-size="12" font-weight="700" fill="{RED}">+</text>')
add(f'<text x="{RAILX-6}" y="{RAILY+32}" text-anchor="end" font-size="12" font-weight="700" fill="{BLK}">−</text>')
# rail holes
plus_holes=[]; gnd_holes=[]
for i in range(24):
    x = RAILX+20+i*26
    hole(x, RAILY+12, 2.6, "#c33"); plus_holes.append((x,RAILY+12))
    hole(x, RAILY+28, 2.6, "#333"); gnd_holes.append((x,RAILY+28))
def Pp(i): return plus_holes[i]
def Pg(i): return gnd_holes[i]

# feed rails from Arduino
wire(P5V[0], P5V[1], Pp(0)[0], Pp(0)[1], RED, mid=(P5V[0], RAILY+12))
wire(GND1[0], GND1[1], Pg(0)[0], Pg(0)[1], BLK, mid=(GND1[0], RAILY+28))

# =========================================================
#  COMPONENT: DHT22  (top center)
# =========================================================
def comp_box(x,y,w,h,fill,stroke,title,sub):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    add(f'<text x="{x+w/2}" y="{y+22}" text-anchor="middle" font-size="14" font-weight="800" fill="#0f172a">{title}</text>')
    add(f'<text x="{x+w/2}" y="{y+40}" text-anchor="middle" font-size="11" fill="#475569">{sub}</text>')

# DHT22 module (blue) with 3 legs: + DATA -
DHTX, DHTY = 470, 90
add(f'<rect x="{DHTX}" y="{DHTY}" width="90" height="70" rx="6" fill="#2f9fe0" stroke="#1f6fa0"/>')
add(f'<g>{"".join("")}</g>')
for r in range(5):
    for c in range(6):
        hole(DHTX+18+c*10, DHTY+12+r*8, 1.6, "#1a5f86")
add(f'<text x="{DHTX+45}" y="{DHTY-8}" text-anchor="middle" font-size="13" font-weight="800" fill="#0f172a">DHT22</text>')
dht_plus=(DHTX+22, DHTY+70); dht_data=(DHTX+45, DHTY+70); dht_gnd=(DHTX+68, DHTY+70)
for px,lbl,col in [(dht_plus,"+","#c33"),(dht_data,"S",YEL),(dht_gnd,"−","#333")]:
    add(f'<rect x="{px[0]-3}" y="{px[1]}" width="6" height="16" fill="#999"/>')
    add(f'<text x="{px[0]}" y="{px[1]+30}" text-anchor="middle" font-size="10" fill="#475569">{lbl}</text>')
# wires: +→rail+, data→D2, −→rail−
wire(dht_plus[0], dht_plus[1]+16, Pp(2)[0], Pp(2)[1], RED, mid=(dht_plus[0], RAILY-10))
wire(dht_data[0], dht_data[1]+16, D2[0], D2[1], YEL, mid=(dht_data[0], 250))
wire(dht_gnd[0], dht_gnd[1]+16, Pg(2)[0], Pg(2)[1], BLK, mid=(dht_gnd[0], RAILY-2))

# =========================================================
#  COMPONENT: LDR voltage divider on a mini breadboard
# =========================================================
BBX, BBY, BBW, BBH = 640, 80, 200, 130
add(f'<rect x="{BBX}" y="{BBY}" width="{BBW}" height="{BBH}" rx="8" fill="#eef0f3" stroke="#cfd4da"/>')
# breadboard holes grid
cols=14; rows=8
for r in range(rows):
    for c in range(cols):
        hole(BBX+14+c*13, BBY+16+r*13, 2.2, "#b9bec6")
def bb(c,r): return (BBX+14+c*13, BBY+16+r*13)
add(f'<text x="{BBX+BBW/2}" y="{BBY-8}" text-anchor="middle" font-size="13" font-weight="800" fill="#0f172a">LDR + R 10kΩ (chia áp → A0)</text>')
# LDR symbol (top, between 5V and node)
ldr_top=bb(3,1); ldr_bot=bb(3,3)
add(f'<rect x="{ldr_top[0]-6}" y="{ldr_top[1]}" width="12" height="{ldr_bot[1]-ldr_top[1]}" rx="6" fill="#caa46a" stroke="#8a6d3b"/>')
add(f'<text x="{ldr_top[0]-14}" y="{(ldr_top[1]+ldr_bot[1])/2}" text-anchor="end" font-size="9" fill="#475569">LDR</text>')
# resistor 10k (node to GND)
r_top=bb(3,4); r_bot=bb(3,6)
add(f'<rect x="{r_top[0]-5}" y="{r_top[1]}" width="10" height="{r_bot[1]-r_top[1]}" rx="3" fill="#d9c9a3" stroke="#b08d57"/>')
add(f'<text x="{r_top[0]+12}" y="{(r_top[1]+r_bot[1])/2}" font-size="9" fill="#475569">10k</text>')
node=bb(3,3)  # middle node (between LDR and R) -> A0
# wires: top of LDR -> 5V rail ; node -> A0 ; bottom of R -> GND rail
wire(ldr_top[0], ldr_top[1], Pp(10)[0], Pp(10)[1], RED, mid=(ldr_top[0], RAILY-20))
wire(node[0]+6, node[1], A0[0], A0[1], YEL, mid=(node[0]+120, 470))
wire(r_bot[0], r_bot[1], Pg(10)[0], Pg(10)[1], BLK, mid=(r_bot[0]+30, RAILY-6))

# =========================================================
#  COMPONENT: LED + 220R on a mini breadboard
# =========================================================
LBX, LBY, LBW, LBH = 900, 80, 200, 130
add(f'<rect x="{LBX}" y="{LBY}" width="{LBW}" height="{LBH}" rx="8" fill="#eef0f3" stroke="#cfd4da"/>')
for r in range(8):
    for c in range(14):
        hole(LBX+14+c*13, LBY+16+r*13, 2.2, "#b9bec6")
def lb(c,r): return (LBX+14+c*13, LBY+16+r*13)
add(f'<text x="{LBX+LBW/2}" y="{LBY-8}" text-anchor="middle" font-size="13" font-weight="800" fill="#0f172a">LED + R 220Ω (→ D7)</text>')
# LED (red) anode top
led_a=lb(7,1); led_k=lb(7,3)
add(f'<circle cx="{led_a[0]}" cy="{(led_a[1]+led_k[1])/2}" r="9" fill="#ef3b3b" stroke="#a01818"/>')
add(f'<text x="{led_a[0]+14}" y="{(led_a[1]+led_k[1])/2}" font-size="9" fill="#475569">LED</text>')
# resistor 220 from anode rail to D7 column
res_t=lb(7,3); res_b=lb(7,5)
add(f'<rect x="{res_t[0]-5}" y="{res_t[1]}" width="10" height="{res_b[1]-res_t[1]}" rx="3" fill="#e6d2b5" stroke="#caa46a"/>')
add(f'<text x="{res_t[0]+12}" y="{(res_t[1]+res_b[1])/2}" font-size="9" fill="#475569">220</text>')
# LED chain: D7 --(220R)--> anode --> LED --> cathode --> GND
# resistor bottom connects to D7 (signal); LED cathode connects to GND rail.
wire(res_b[0], res_b[1], D7[0], D7[1], YEL, mid=(res_b[0]-120, 250))
# internal tie: cathode of LED down to a free column, then to GND rail
wire(led_k[0], led_k[1], Pg(20)[0], Pg(20)[1], BLK, mid=(led_k[0]+50, RAILY-8))

# =========================================================
#  COMPONENT: SERVO SG90  (right middle)
# =========================================================
SVX, SVY = 980, 360
add(f'<rect x="{SVX}" y="{SVY}" width="120" height="70" rx="8" fill="#2b6fc2" stroke="#1c4f90"/>')
add(f'<rect x="{SVX+40}" y="{SVY-22}" width="40" height="26" rx="4" fill="#5b9bd5"/>')
add(f'<rect x="{SVX+95}" y="{SVY+20}" width="44" height="10" rx="3" fill="#cdd6e0"/>')  # arm
add(f'<text x="{SVX+60}" y="{SVY+42}" text-anchor="middle" font-size="13" font-weight="800" fill="#fff">Servo SG90</text>')
add(f'<text x="{SVX+60}" y="{SVY+58}" text-anchor="middle" font-size="10" fill="#dbeafe">cửa thông gió</text>')
sv_sig=(SVX, SVY+18); sv_v=(SVX, SVY+34); sv_g=(SVX, SVY+50)
for py,lbl,col in [(sv_sig,"S",ORN),(sv_v,"+",RED),(sv_g,"−",BLK)]:
    add(f'<text x="{py[0]-8}" y="{py[1]+3}" text-anchor="end" font-size="9" fill="#475569">{lbl}</text>')
# wires: signal->D9, V+->rail+, GND->rail-
wire(sv_sig[0], sv_sig[1], D9[0], D9[1], ORN, mid=(700, sv_sig[1]))
wire(sv_v[0], sv_v[1], Pp(22)[0], Pp(22)[1], RED, mid=(SVX-40, 320))
wire(sv_g[0], sv_g[1], Pg(22)[0], Pg(22)[1], BLK, mid=(SVX-60, 330))

# =========================================================
#  COMPONENT: LCD1602 + I2C  (bottom center)
# =========================================================
LCX, LCY = 470, 560
add(f'<rect x="{LCX}" y="{LCY}" width="300" height="120" rx="8" fill="#0f3d2e" stroke="#0a2a20"/>')
add(f'<rect x="{LCX+20}" y="{LCY+24}" width="260" height="72" rx="4" fill="#8fd14f"/>')   # green screen
# I2C backpack on the back-left
add(f'<rect x="{LCX-4}" y="{LCY+12}" width="44" height="40" rx="3" fill="#111"/>')
lcd_g=(LCX+4, LCY+58); lcd_v=(LCX+14, LCY+58); lcd_sda=(LCX+24, LCY+58); lcd_scl=(LCX+34, LCY+58)
for px,lbl in [(lcd_g,"G"),(lcd_v,"V"),(lcd_sda,"SDA"),(lcd_scl,"SCL")]:
    add(f'<rect x="{px[0]-2}" y="{LCY+52}" width="4" height="14" fill="#999"/>')
    add(f'<text x="{px[0]}" y="{LCY+80}" text-anchor="middle" font-size="8" fill="#cbd5e1">{lbl}</text>')
add(f'<text x="{LCX+150}" y="{LCY+114}" text-anchor="middle" font-size="13" font-weight="800" fill="#d1fae5">LCD1602 + I2C  (0x27)</text>')
# wires: V->rail+, G->rail-, SDA->A4, SCL->A5
wire(lcd_v[0], lcd_v[1]+14, Pp(4)[0], Pp(4)[1], RED, mid=(lcd_v[0]-40, 420))
wire(lcd_g[0], lcd_g[1]+14, Pg(4)[0], Pg(4)[1], BLK, mid=(lcd_g[0]-60, 420))
wire(lcd_sda[0], lcd_sda[1]+14, A4[0], A4[1], BLU, mid=(A4[0], 560))
wire(lcd_scl[0], lcd_scl[1]+14, A5[0], A5[1], BLU, mid=(A5[0]+40, 560))

# =========================================================
#  COMPONENT: Buzzer (Layer 3 — fire alarm)  on Arduino D8
# =========================================================
BZX, BZY = 820, 470
add(f'<circle cx="{BZX+30}" cy="{BZY+30}" r="30" fill="#1f2937" stroke="#0b1220" stroke-width="2"/>')
add(f'<circle cx="{BZX+30}" cy="{BZY+30}" r="6" fill="#0b1220"/>')
add(f'<text x="{BZX+30}" y="{BZY+78}" text-anchor="middle" font-size="13" font-weight="800" fill="#0f172a">Buzzer 🔊</text>')
add(f'<text x="{BZX+30}" y="{BZY+94}" text-anchor="middle" font-size="10" fill="#475569">còi báo cháy → D8</text>')
bz_pos=(BZX+16, BZY+58); bz_neg=(BZX+44, BZY+58)
add(f'<text x="{bz_pos[0]}" y="{bz_pos[1]+6}" text-anchor="middle" font-size="10" fill="#b91c1c">+</text>')
add(f'<text x="{bz_neg[0]}" y="{bz_neg[1]+6}" text-anchor="middle" font-size="10" fill="#111">−</text>')
# wires: + -> D8, - -> GND rail
wire(bz_pos[0], bz_pos[1], D8[0], D8[1], YEL, mid=(bz_pos[0]-120, 250))
wire(bz_neg[0], bz_neg[1], Pg(18)[0], Pg(18)[1], BLK, mid=(bz_neg[0]+30, RAILY-6))

# =========================================================
#  PI 4-DIGIT callout (Layer 3 — lives on the Raspberry Pi, not Arduino)
# =========================================================
PDX, PDY = 820, 600
zone(PDX-12, PDY-26, 320, 118, L2, "#d9770612")  # reuse amber-ish zone style
add(f'<rect x="{PDX}" y="{PDY}" width="240" height="60" rx="8" fill="#111827" stroke="#374151"/>')
for i in range(4):
    add(f'<rect x="{PDX+18+i*54}" y="{PDY+12}" width="36" height="36" rx="3" fill="#7f1d1d"/>')
    add(f'<text x="{PDX+36+i*54}" y="{PDY+38}" text-anchor="middle" font-size="22" font-weight="800" fill="#fca5a5">{["2","7","5","C"][i]}</text>')
add(f'<text x="{PDX+120}" y="{PDY+78}" text-anchor="middle" font-size="12" font-weight="800" fill="#9a3412">LED 4-digit → nối thẳng RASPBERRY PI (74HC595, GPIO 3.3V)</text>')

# =========================================================
#  USB-to-Pi callout
# =========================================================
add(f'<rect x="{AX-30}" y="{AY+AH+24}" width="380" height="44" rx="10" fill="#fff7ed" stroke="{ORN}" stroke-width="2"/>')
add(f'<text x="{AX-14}" y="{AY+AH+50}" font-size="13" font-weight="800" fill="#9a3412">⎘ CÁP USB → Raspberry Pi (/dev/ttyACM0)</text>')
add(f'<text x="{AX-14}" y="{AY+AH+64}" font-size="11" fill="#9a5a36">Cắm USB Arduino vào cổng USB của Pi. KHÔNG nối TX/RX.</text>')

# ---------- two-layer strategy note ----------
NY = 780
add(f'<rect x="28" y="{NY}" width="1124" height="92" rx="12" fill="#f8fafc" stroke="#cbd5e1"/>')
add(f'<rect x="28" y="{NY}" width="10" height="92" rx="5" fill="{L1}"/>')
add(f'<text x="52" y="{NY+24}" font-size="13.5" font-weight="800" fill="#166534">🟢 LAYER 1 (lắp trước, ~8đ):</text>')
add(f'<text x="270" y="{NY+24}" font-size="12.5" fill="#334155">DHT22 (D2) + LDR (A0) + LED (D7) + cáp USB → Pi → Flask. Ít dây, khó hỏng.</text>')
add(f'<text x="52" y="{NY+48}" font-size="13.5" font-weight="800" fill="#b45309">🟡 LAYER 2 (tăng điểm):</text>')
add(f'<text x="270" y="{NY+48}" font-size="12.5" fill="#334155">Servo cửa thông gió (D9) + LCD1602 I2C (A4/A5). Mỗi phần độc lập, tháo được.</text>')
add(f'<text x="52" y="{NY+72}" font-size="13.5" font-weight="800" fill="#991b1b">🔴 LAYER 3 (ăn điểm):</text>')
add(f'<text x="270" y="{NY+72}" font-size="12.5" fill="#334155">Buzzer báo cháy (D8, temp≥50°C) + LED 4-digit trên RASPBERRY PI (74HC595, GPIO 3.3V).</text>')

add('</svg>')

out = "/Users/bnqtoan/MSE/iot/final/docs/wiring-breadboard.svg"
with open(out,"w") as f:
    f.write("\n".join(parts))
print("wrote", out)
