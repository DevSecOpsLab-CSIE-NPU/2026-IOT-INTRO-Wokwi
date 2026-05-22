from machine import Pin, I2C
import sh1107
import dht
import time
import math
import framebuf

# =========================================================
# Week 13 Homework
# SH1107 + DHT22 中文動畫溫度看板
# 學號：1114405029
#
# 注意：
# make.bat 會把 goku_bitmap.py 合併到 main.py 前面。
# 所以這裡不要 import goku_bitmap。
# =========================================================

i2c = I2C(0, scl=Pin(21), sda=Pin(22))

oled = sh1107.SH1107_I2C(
    128,
    128,
    i2c,
    address=0x3C,
    rotate=90
)

dht_sensor = dht.DHT22(Pin(23))

temperature = 0.0
humidity = 0.0
sensor_ok = False

frame = 0
last_sensor_read = 0
start_time = time.ticks_ms()

ANIMATION_DELAY_MS = 120
SENSOR_INTERVAL_MS = 2000
SWITCH_INTERVAL_MS = 2000

# =========================================================
# 建立悟空 FrameBuffer
# =========================================================

actual_goku_height = (len(goku_bitmap) * 8) // goku_width

if actual_goku_height < goku_height:
    goku_height = actual_goku_height

goku_fb = framebuf.FrameBuffer(
    goku_bitmap,
    goku_width,
    goku_height,
    framebuf.MONO_VLSB
)

# =========================================================
# 小字型：學號用
# =========================================================

FONT_3X5 = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
    "I": ("111", "010", "010", "010", "111"),
    "D": ("110", "101", "101", "101", "110"),
    ":": ("000", "010", "000", "010", "000"),
    " ": ("000", "000", "000", "000", "000"),
}

def draw_tiny_text(display, text, x, y):
    cursor_x = x

    for ch in text:
        glyph = FONT_3X5.get(ch, FONT_3X5[" "])

        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    px = cursor_x + col
                    py = y + row

                    if 0 <= px < 128 and 0 <= py < 128:
                        display.pixel(px, py, 1)

        cursor_x += 4

# =========================================================
# 中文點陣資料：花、火、節
# =========================================================

FONT_82B1 = bytearray(
    b'\x00\x00\x00\x00\x00\x7c\x1e\x00\x00\x78\x1c\x10'
    b'\x00\x78\x1c\x18\x00\x78\x1c\x3c\x7f\xff\xff\xfe'
    b'\x00\x78\x1c\x00\x00\x78\x1c\x00\x00\x78\x1c\x00'
    b'\x00\x00\x00\x00\x00\xf0\xf8\x00\x00\xf8\xf0\x00'
    b'\x01\xf0\xf0\x70\x01\xe0\xf0\xf8\x03\xc0\xf1\xf0'
    b'\x03\xc0\xf1\xe0\x07\xe0\xf3\xc0\x0f\xe0\xf7\x00'
    b'\x0d\xe0\xfc\x00\x19\xe0\xf0\x00\x31\xe0\xf0\x00'
    b'\x41\xe0\xf0\x00\x01\xe0\xf0\x04\x01\xe0\xf0\x04'
    b'\x01\xe0\xf0\x04\x01\xe0\xf0\x0c\x01\xe0\xf0\x0c'
    b'\x01\xe0\xff\xfe\x01\xe0\xff\xfe\x01\xe0\x7f\xfe'
    b'\x01\xc0\x0f\xe0\x00\x00\x00\x00'
)

FONT_706B = bytearray(
    b'\x00\x00\x00\x00\x00\x07\x00\x00\x00\x07\x80\x00'
    b'\x00\x07\x80\x00\x00\x07\x80\x00\x00\x07\x80\x00'
    b'\x00\x07\x80\x00\x01\x07\x80\x60\x01\x07\x80\xf0'
    b'\x01\x87\xc0\xfc\x01\x87\xc1\xf0\x03\x87\xc3\xe0'
    b'\x03\x87\xc3\xc0\x07\x8f\x47\x00\x0f\x8f\x6e\x00'
    b'\x1f\x0f\x68\x00\x1f\x0f\x30\x00\x1e\x0f\x30\x00'
    b'\x00\x1e\x30\x00\x00\x1e\x38\x00\x00\x1e\x1c\x00'
    b'\x00\x3c\x1e\x00\x00\x38\x1e\x00\x00\x78\x0f\x80'
    b'\x00\xf0\x0f\xc0\x01\xe0\x07\xf0\x03\xc0\x03\xfc'
    b'\x07\x00\x01\xfe\x0e\x00\x00\xf8\x18\x00\x00\x70'
    b'\x40\x00\x00\x10\x00\x00\x00\x00'
)

FONT_7BC0 = bytearray(
    b'\x07\x80\x38\x00\x07\x84\x7c\x18\x07\x0e\x78\x3c'
    b'\x0f\xff\x7f\xfe\x0e\xe0\xe7\x00\x1c\x70\xc3\x80'
    b'\x18\x71\x83\xc0\x30\x71\x03\xc0\x60\x74\x01\x90'
    b'\x0c\x0e\x38\x38\x0f\xff\x3f\xfc\x0e\x0f\x38\x3c'
    b'\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c\x0f\xff\x38\x3c'
    b'\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c'
    b'\x0e\x0f\x38\x3c\x0f\xff\x38\x3c\x0e\x0e\x38\x3c'
    b'\x0e\x20\x38\x3c\x0e\x38\x38\x3c\x0e\x1c\x38\xf8'
    b'\x0e\x1e\x38\x78\x1f\xff\x38\x78\x7f\xc7\x38\x60'
    b'\x7f\x07\x38\x00\x3c\x07\x38\x00\x20\x00\x38\x00'
    b'\x00\x00\x30\x00\x00\x00\x00\x00'
)

CHARS = {
    "HUA": (FONT_82B1, 32, 32),
    "HUO": (FONT_706B, 32, 32),
    "JIE": (FONT_7BC0, 32, 32),
}

def glyph_pixel(data, width, x, y):
    row_bytes = (width + 7) // 8
    value = data[y * row_bytes + x // 8]
    return (value >> (7 - (x % 8))) & 1

def draw_char(display, char_key, x, y, shrink=2):
    if char_key not in CHARS:
        return

    data, w, h = CHARS[char_key]
    out_w = (w + shrink - 1) // shrink
    out_h = (h + shrink - 1) // shrink

    for oy in range(out_h):
        sy = oy * shrink

        for ox in range(out_w):
            sx = ox * shrink

            if glyph_pixel(data, w, sx, sy):
                px = x + ox
                py = y + oy

                if 0 <= px < 128 and 0 <= py < 128:
                    display.pixel(px, py, 1)

# =========================================================
# 基本繪圖
# =========================================================

def draw_char_big(display, char_key, x, y):
    # shrink=1 是原始 32x32 大小
    # 這裡只畫一次，用來做「突然放大」效果
    draw_char(display, char_key, x, y, 1)

def draw_pixel_line(display, x0, y0, x1, y1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    err = dx + dy

    while True:
        if 0 <= x0 < 128 and 0 <= y0 < 128:
            display.pixel(x0, y0, 1)

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err

        if e2 >= dy:
            err += dy
            x0 += sx

        if e2 <= dx:
            err += dx
            y0 += sy

def draw_circle(display, cx, cy, r):
    x = r
    y = 0
    err = 0

    while x >= y:
        points = [
            (cx + x, cy + y),
            (cx + y, cy + x),
            (cx - y, cy + x),
            (cx - x, cy + y),
            (cx - x, cy - y),
            (cx - y, cy - x),
            (cx + y, cy - x),
            (cx + x, cy - y),
        ]

        for px, py in points:
            if 0 <= px < 128 and 0 <= py < 128:
                display.pixel(px, py, 1)

        y += 1

        if err <= 0:
            err += 2 * y + 1

        if err > 0:
            x -= 1
            err -= 2 * x + 1

def draw_star(display, cx, cy, size, angle_deg):
    points = []

    for i in range(10):
        angle = math.radians(angle_deg + i * 36 - 90)

        if i % 2 == 0:
            radius = size
        else:
            radius = size // 2

        px = cx + int(math.cos(angle) * radius)
        py = cy + int(math.sin(angle) * radius)

        points.append((px, py))

    for i in range(10):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % 10]
        draw_pixel_line(display, x1, y1, x2, y2)

# =========================================================
# DHT22 安全讀取
# =========================================================

def read_sensor_safe():
    global temperature, humidity, sensor_ok

    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        sensor_ok = True

        print("[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%".format(
            temperature,
            humidity
        ))

    except Exception as e:
        sensor_ok = False
        print("[ERROR] DHT22 read failed:", e)

# =========================================================
# 畫面區塊
# =========================================================

def draw_fixed_info(display):
    # 參考圖左上英文資訊區
    display.text("PENGHU", 0, 0)
    display.text("SCI TECH", 0, 10)
    display.text("CSIE", 0, 20)
    draw_tiny_text(display, "ID:1114405029", 0, 32)
    display.text("2026", 60, 0)

def draw_temperature(display):
    # 溫濕度放下方，不干擾中央主視覺
    if sensor_ok:
        display.text("{:.1f} C".format(temperature), 0, 104)
        display.text("H:{:.0f}%".format(humidity), 0, 116)
    else:
        display.text("Sensor", 0, 104)
        display.text("Error", 0, 116)

def draw_fireworks(display, frame):
    phase = frame % 12

    # 左側煙火動畫
    cx = 8
    cy = 58
    r = 4 + phase

    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x2 = cx + int(math.cos(rad) * r)
        y2 = cy + int(math.sin(rad) * r)
        draw_pixel_line(display, cx, cy, x2, y2)

    # 左下小煙火
    cx2 = 8
    cy2 = 92
    r2 = 4 + ((phase + 5) % 8)

    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x2 = cx2 + int(math.cos(rad) * r2)
        y2 = cy2 + int(math.sin(rad) * r2)
        draw_pixel_line(display, cx2, cy2, x2, y2)

    # 發射尾巴
    for i in range(9):
        x = 8 + i // 4
        y = 98 - i * 3

        if 0 <= x < 128 and 0 <= y < 128:
            display.pixel(x, y, 1)

    # 閃爍星點
    if frame % 2 == 0:
        stars = [
            (10, 42), (24, 46),
            (10, 76), (26, 82),
            (10, 106), (28, 110),
        ]

        for x, y in stars:
            display.pixel(x, y, 1)
            if x + 1 < 128:
                display.pixel(x + 1, y, 1)

def draw_chinese_animation(display, frame):
    draw_fireworks(display, frame)

    wave = int(math.sin(frame * 0.25) * 2)

    # 0 放大「花」、1 放大「火」、2 放大「節」
    big_index = (time.ticks_ms() // 2000) % 3

    if big_index == 0:
        draw_char(display, "HUA", 66, 38 + wave, 1)
    else:
        draw_char(display, "HUA", 74, 48 + wave, 2)

    if big_index == 1:
        draw_char(display, "HUO", 66, 60 - wave, 1)
    else:
        draw_char(display, "HUO", 74, 72 - wave, 2)

    if big_index == 2:
        draw_char(display, "JIE", 66, 82 + wave, 1)
    else:
        draw_char(display, "JIE", 74, 96 + wave, 2)

def draw_dragon_effect(display, frame):
    # 中央主視覺：龍珠圓 + 星
    center_x = 28
    center_y = 68

    pulse = int(math.sin(frame * 0.30) * 2)

    draw_circle(display, center_x, center_y, 29 + pulse)
    draw_circle(display, center_x, center_y, 24 + pulse)

    if temperature >= 28:
        temp_level = 3
    elif temperature >= 24:
        temp_level = 1
    else:
        temp_level = -1

    draw_star(
        display,
        center_x,
        center_y,
        11 + max(0, pulse) + temp_level,
        frame * 16
    )

    # 龍珠周圍亮點動畫
    for i in range(8):
        a = math.radians(frame * 16 + i * 45)
        sx = center_x + int(math.cos(a) * (34 + pulse))
        sy = center_y + int(math.sin(a) * (34 + pulse))

        if 0 <= sx < 128 and 0 <= sy < 128:
            display.pixel(sx, sy, 1)

def draw_goku_effect(display, frame):
    # 悟空放在中央主視覺區，和龍珠模式交替
    goku_x = 2
    goku_y = 42 + int(math.sin(frame * 0.20) * 1)

    display.blit(goku_fb, goku_x, goku_y)

    if frame % 2 == 0:
        sparks = [
            (42, 42), (104, 44),
            (44, 88), (106, 90),
            (74, 38), (74, 104),
        ]

        for sx, sy in sparks:
            if 0 <= sx < 128 and 0 <= sy < 128:
                display.pixel(sx, sy, 1)
                if sx + 1 < 128:
                    display.pixel(sx + 1, sy, 1)

# =========================================================
# 主程式
# =========================================================

read_sensor_safe()
last_sensor_read = time.ticks_ms()
start_time = time.ticks_ms()

while True:
    now = time.ticks_ms()

    # 每 2 秒讀一次 DHT22
    if time.ticks_diff(now, last_sensor_read) >= SENSOR_INTERVAL_MS:
        read_sensor_safe()
        last_sensor_read = now

    oled.fill(0)

    # A. 靜態資訊
    draw_fixed_info(oled)

    # B. 中文與煙火動畫
    draw_chinese_animation(oled, frame)

    # C. 中央主視覺動畫：龍珠 / 悟空交替
    elapsed = time.ticks_diff(now, start_time)
    mode = (elapsed // SWITCH_INTERVAL_MS) % 2

    if mode == 0:
        draw_dragon_effect(oled, frame)
    else:
        draw_goku_effect(oled, frame)

    # D. 溫濕度資訊
    draw_temperature(oled)

    oled.show()

    frame += 1
    time.sleep_ms(ANIMATION_DELAY_MS)