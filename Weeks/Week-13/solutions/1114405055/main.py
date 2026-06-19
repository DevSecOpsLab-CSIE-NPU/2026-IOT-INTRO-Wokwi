from machine import Pin, I2C
import sh1107
import dht
import time

# ---------------------------------------------------------------------------
# Week 13 Homework: SH1107 + DHT22 Chinese animated temperature dashboard
# Layout / Chinese-glyph / wrap-y design follows in-class/task3a (dragon ball
# + English info block + "花火節" vertical dancing animation), extended with
# a DHT22-driven temperature block and a student-id row (task4 integration).
# ---------------------------------------------------------------------------

STUDENT_ID = "1114405055"

# ESP32 I2C pin assignment for Grove SH1107 OLED (match diagram.json wiring)
i2c = I2C(0, scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 128
oled = sh1107.SH1107_I2C(oled_width, oled_height, i2c, address=0x3C, rotate=90)

# --- tunable calibration constants (kept adjustable per HOMEWORK 技術限制) ---
center_x = 64
center_y = 64
offset = 8                       # general layout breathing room
dragon_center_x = center_x - 24  # dragon-ball (circle + star) center
dragon_center_y = center_y + 6
chinese_base_x = 96              # vertical "花火節" column anchor
chinese_base_y = 22
temp_box_y = 104                 # top edge of the temperature block

SENSOR_INTERVAL_MS = 2000        # read DHT22 every 2 seconds
FRAME_INTERVAL_MS = 250          # redraw/animate every 250 ms

# DHT22 data pin (match diagram.json wiring)
dht_sensor = dht.DHT22(Pin(23))


# ---------------------------------------------------------------------------
# Chinese glyph data: 32x32 1bpp bitmaps for 花 火 節 (MSB-first rows)
# ---------------------------------------------------------------------------
FONT_82B1 = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x0C, 0x03, 0x80, 0x00, 0x0E, 0x03, 0x00, 0x00, 0x06, 0x03, 0x60, 0x00, 0x07, 0xC7, 0xF0, 0x00, 0x7E, 0x1E, 0x00, 0x00, 0x3B, 0x04, 0x00, 0x00, 0x01, 0x04, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x03, 0x10, 0x00, 0x00, 0x07, 0x18, 0x00, 0x00, 0x06, 0x18, 0x00, 0x00, 0x0C, 0x18, 0x00, 0x00, 0x18, 0x18, 0x70, 0x00, 0x1C, 0x1F, 0xF0, 0x00, 0x24, 0x1E, 0x00, 0x00, 0x44, 0x10, 0x00, 0x01, 0x84, 0x10, 0x00, 0x02, 0x0C, 0x10, 0x02, 0x00, 0x0C, 0x10, 0x02, 0x00, 0x0C, 0x18, 0x02, 0x00, 0x0C, 0x1C, 0x07, 0x00, 0x0C, 0x0F, 0xFF, 0x00, 0x0C, 0x07, 0xFE, 0x00, 0x0C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # 花
FONT_706B = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x03, 0x80, 0x00, 0x00, 0x03, 0x80, 0x00, 0x00, 0x03, 0x80, 0x00, 0x00, 0x03, 0x80, 0x00, 0x00, 0x03, 0x83, 0x00, 0x00, 0x03, 0x87, 0x80, 0x00, 0xC3, 0x8E, 0x00, 0x00, 0xE3, 0x0C, 0x00, 0x00, 0x63, 0x18, 0x00, 0x00, 0x73, 0x60, 0x00, 0x00, 0x23, 0x80, 0x00, 0x00, 0x03, 0x80, 0x00, 0x00, 0x03, 0xC0, 0x00, 0x00, 0x06, 0x60, 0x00, 0x00, 0x06, 0x30, 0x00, 0x00, 0x06, 0x30, 0x00, 0x00, 0x0C, 0x1C, 0x00, 0x00, 0x18, 0x0E, 0x00, 0x00, 0x30, 0x0F, 0x00, 0x00, 0x60, 0x07, 0xC0, 0x01, 0xC0, 0x03, 0xF0, 0x06, 0x00, 0x01, 0xFC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # 火
FONT_7BC0 = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x60, 0x00, 0x01, 0xC0, 0xE0, 0x00, 0x01, 0x80, 0xDF, 0x00, 0x03, 0xF8, 0xF8, 0x00, 0x03, 0x01, 0x80, 0x00, 0x06, 0x03, 0x30, 0x00, 0x0C, 0xE2, 0x18, 0x00, 0x08, 0x64, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x38, 0x00, 0x00, 0x07, 0xFD, 0x1E, 0x00, 0x06, 0x19, 0xE7, 0x00, 0x06, 0x59, 0x82, 0x00, 0x07, 0xF9, 0x86, 0x00, 0x06, 0x11, 0x86, 0x00, 0x06, 0x11, 0x86, 0x00, 0x07, 0xF1, 0x86, 0x00, 0x06, 0x01, 0x86, 0x00, 0x06, 0x31, 0x9E, 0x00, 0x06, 0x39, 0x8E, 0x00, 0x06, 0xD9, 0x84, 0x00, 0x07, 0x89, 0x80, 0x00, 0x07, 0x01, 0x80, 0x00, 0x06, 0x01, 0x80, 0x00, 0x00, 0x01, 0x80, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # 節

CHARS = {
    '花': (FONT_82B1, 32, 32),
    '火': (FONT_706B, 32, 32),
    '節': (FONT_7BC0, 32, 32),
}


def glyph_pixel(data, width, x, y):
    row_bytes = (width + 7) // 8
    value = data[y * row_bytes + x // 8]
    return (value >> (7 - (x % 8))) & 1


def draw_char_pixels(display, char, x, y, shrink=1, wrap_y=False):
    data, w, h = CHARS[char]
    out_w = w // shrink
    out_h = h // shrink
    for oy in range(out_h):
        for ox in range(out_w):
            if glyph_pixel(data, w, ox * shrink, oy * shrink):
                px = x + ox
                py = y + oy
                if wrap_y:
                    py %= oled_height
                if 0 <= px < oled_width and 0 <= py < oled_height:
                    display.pixel(px, py, 1)


def draw_dancing_chinese(display, frame, base_x, base_y):
    """3 個中文字依序放大 2 倍並做波浪舞，跨越底部時 wrap 回頂部。"""
    chars = "花火節"
    spacing = 4
    wave = (-3, 0, 3, 0)
    active = frame % len(chars)
    cy = base_y

    for i, ch in enumerate(chars):
        enlarged = i == active
        shrink = 1 if enlarged else 2
        size = 32 if enlarged else 16
        x = base_x - 8 if enlarged else base_x
        y = cy + wave[(frame + i) % len(wave)]
        if enlarged:
            y -= 8
        draw_char_pixels(display, ch, x, y, shrink=shrink, wrap_y=True)
        cy += size + spacing


def draw_circle(display, cx, cy, r, color=1):
    x = r
    y = 0
    err = 0
    while x >= y:
        display.pixel(cx + x, cy + y, color)
        display.pixel(cx + y, cy + x, color)
        display.pixel(cx - y, cy + x, color)
        display.pixel(cx - x, cy + y, color)
        display.pixel(cx - x, cy - y, color)
        display.pixel(cx - y, cy - x, color)
        display.pixel(cx + y, cy - x, color)
        display.pixel(cx + x, cy - y, color)
        y += 1
        if err <= 0:
            err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1


def draw_star(display, cx, cy, size, color=1):
    pts = [
        (cx, cy - size),
        (cx + int(size * 0.35), cy - int(size * 0.25)),
        (cx + size, cy - int(size * 0.2)),
        (cx + int(size * 0.5), cy + int(size * 0.25)),
        (cx + int(size * 0.6), cy + size),
        (cx, cy + int(size * 0.45)),
        (cx - int(size * 0.6), cy + size),
        (cx - int(size * 0.5), cy + int(size * 0.25)),
        (cx - size, cy - int(size * 0.2)),
        (cx - int(size * 0.35), cy - int(size * 0.25)),
    ]
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        display.line(x1, y1, x2, y2, color)


def draw_static_scene(display):
    """背景：龍珠主視覺 + 英文資訊區塊 + 學號 + 溫度區塊邊框。"""
    display.fill(0)

    # English info block (top-left)
    display.text("Penghu Univ", 2, 0, 1)
    display.text("Dept of CSIE", 2, 9, 1)
    display.text("2026", 104, 0, 1)

    # Student-id row (must be readable on the OLED itself, not just README)
    display.text(STUDENT_ID, 2, 18, 1)

    # Dragon-ball main visual (circle + star)
    draw_circle(display, dragon_center_x, dragon_center_y, 26, 1)
    draw_circle(display, dragon_center_x, dragon_center_y, 23, 1)
    draw_star(display, dragon_center_x, dragon_center_y, 10, 1)

    # Temperature block border
    display.hline(0, temp_box_y, oled_width, 1)


def draw_temperature(display, temp_c, humidity, valid, has_data, y):
    display.text("TEMP", 4, y + 2, 1)
    if has_data:
        display.text("{:.1f} C".format(temp_c), 4, y + 11, 1)
        display.text("{:.0f}%".format(humidity), 92, y + 11, 1)
        if not valid:
            display.text("ERR", 60, y + 2, 1)
    else:
        display.text("Sensor Error", 4, y + 11, 1)


def read_sensor_safe(sensor, last_temp, last_humidity):
    """讀取 DHT22；失敗時印出錯誤並回傳前次有效值，程式不當掉。"""
    try:
        sensor.measure()
        temp_c = sensor.temperature()
        humidity = sensor.humidity()
        print("[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%".format(temp_c, humidity))
        return temp_c, humidity, True
    except Exception as e:
        print("[ERROR] DHT22 read failed:", e)
        return last_temp, last_humidity, False


# ---------------------------------------------------------------------------
# Main loop
# A. 依時間/幀數更新動畫
# B. 每 2 秒讀一次 DHT22（read_sensor_safe）
# C. 重畫整個畫面（背景 + 中文動畫 + 溫度 + 主圖）
# D. oled.show()
# ---------------------------------------------------------------------------
frame = 0
last_temp = 0.0
last_humidity = 0.0
sensor_ok = False
has_data = False
last_read_ms = time.ticks_ms() - SENSOR_INTERVAL_MS  # force an immediate read

while True:
    now = time.ticks_ms()
    if time.ticks_diff(now, last_read_ms) >= SENSOR_INTERVAL_MS:
        last_temp, last_humidity, sensor_ok = read_sensor_safe(dht_sensor, last_temp, last_humidity)
        if sensor_ok:
            has_data = True
        last_read_ms = now

    draw_static_scene(oled)
    draw_dancing_chinese(oled, frame, chinese_base_x, chinese_base_y)
    draw_temperature(oled, last_temp, last_humidity, sensor_ok, has_data, temp_box_y)
    oled.show()

    frame = (frame + 1) % 3
    time.sleep_ms(FRAME_INTERVAL_MS)
