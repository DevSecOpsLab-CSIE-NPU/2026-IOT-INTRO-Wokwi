from machine import Pin, I2C
import dht
import sh1107
import time

# ------------------------------
# Tunable constants
# ------------------------------
I2C_ID = 0
I2C_SCL_PIN = 18
I2C_SDA_PIN = 19
DHT22_PIN = 22

OLED_WIDTH = 128
OLED_HEIGHT = 128
OLED_ROTATE = 90

# Visual calibration constants required by homework
center_x = 64
center_y = 64
offset_x = -32
offset_y = 0
text_y_offset = 0

ANIM_INTERVAL_MS = 250
SENSOR_INTERVAL_MS = 2000


i2c = I2C(I2C_ID, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))
oled = sh1107.SH1107_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, address=0x3C, rotate=OLED_ROTATE)
sensor = dht.DHT22(Pin(DHT22_PIN))


def dragon_x():
    return center_x + offset_x


def dragon_y():
    return center_y + offset_y


def ty(y):
    return y + text_y_offset


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


FONT_3X5 = {
    "A": ("111", "101", "111", "101", "101"),
    "B": ("110", "101", "110", "101", "110"),
    "C": ("111", "100", "100", "100", "111"),
    "D": ("110", "101", "101", "101", "110"),
    "E": ("111", "100", "110", "100", "111"),
    "F": ("111", "100", "110", "100", "100"),
    "G": ("111", "100", "101", "101", "111"),
    "H": ("101", "101", "111", "101", "101"),
    "I": ("111", "010", "010", "010", "111"),
    "L": ("100", "100", "100", "100", "111"),
    "N": ("101", "111", "111", "111", "101"),
    "O": ("111", "101", "101", "101", "111"),
    "P": ("111", "101", "111", "100", "100"),
    "R": ("111", "101", "111", "110", "101"),
    "S": ("111", "100", "111", "001", "111"),
    "T": ("111", "010", "010", "010", "010"),
    "U": ("101", "101", "101", "101", "111"),
    "V": ("101", "101", "101", "101", "010"),
    "Y": ("101", "101", "010", "010", "010"),
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "001", "001", "001"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
    ":": ("000", "010", "000", "010", "000"),
    ".": ("000", "000", "000", "000", "010"),
    "%": ("101", "001", "010", "100", "101"),
    "-": ("000", "000", "111", "000", "000"),
    " ": ("000", "000", "000", "000", "000"),
    "?": ("111", "001", "011", "000", "010"),
}


def draw_tiny_text(display, text, x, y, color=1):
    cursor_x = x
    for ch in text.upper():
        glyph = FONT_3X5.get(ch, FONT_3X5["?"])
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    display.pixel(cursor_x + col, y + row, color)
        cursor_x += 4


FONT_82B1 = bytearray(
    b"\x00\x00\x00\x00\x00\x7c\x1e\x00\x00\x78\x1c\x10"
    b"\x00\x78\x1c\x18\x00\x78\x1c\x3c\x7f\xff\xff\xfe"
    b"\x00\x78\x1c\x00\x00\x78\x1c\x00\x00\x78\x1c\x00"
    b"\x00\x00\x00\x00\x00\xf0\xf8\x00\x00\xf8\xf0\x00"
    b"\x01\xf0\xf0\x70\x01\xe0\xf0\xf8\x03\xc0\xf1\xf0"
    b"\x03\xc0\xf1\xe0\x07\xe0\xf3\xc0\x0f\xe0\xf7\x00"
    b"\x0d\xe0\xfc\x00\x19\xe0\xf0\x00\x31\xe0\xf0\x00"
    b"\x41\xe0\xf0\x00\x01\xe0\xf0\x04\x01\xe0\xf0\x04"
    b"\x01\xe0\xf0\x04\x01\xe0\xf0\x0c\x01\xe0\xf0\x0c"
    b"\x01\xe0\xff\xfe\x01\xe0\xff\xfe\x01\xe0\x7f\xfe"
    b"\x01\xc0\x0f\xe0\x00\x00\x00\x00"
)

FONT_706B = bytearray(
    b"\x00\x00\x00\x00\x00\x07\x00\x00\x00\x07\x80\x00"
    b"\x00\x07\x80\x00\x00\x07\x80\x00\x00\x07\x80\x00"
    b"\x00\x07\x80\x00\x01\x07\x80\x60\x01\x07\x80\xf0"
    b"\x01\x87\xc0\xfc\x01\x87\xc1\xf0\x03\x87\xc3\xe0"
    b"\x03\x87\xc3\xc0\x07\x8f\x47\x00\x0f\x8f\x6e\x00"
    b"\x1f\x0f\x68\x00\x1f\x0f\x30\x00\x1e\x0f\x30\x00"
    b"\x00\x1e\x30\x00\x00\x1e\x38\x00\x00\x1e\x1c\x00"
    b"\x00\x3c\x1e\x00\x00\x38\x1e\x00\x00\x78\x0f\x80"
    b"\x00\xf0\x0f\xc0\x01\xe0\x07\xf0\x03\xc0\x03\xfc"
    b"\x07\x00\x01\xfe\x0e\x00\x00\xf8\x18\x00\x00\x70"
    b"\x40\x00\x00\x10\x00\x00\x00\x00"
)

FONT_7BC0 = bytearray(
    b"\x07\x80\x38\x00\x07\x84\x7c\x18\x07\x0e\x78\x3c"
    b"\x0f\xff\x7f\xfe\x0e\xe0\xe7\x00\x1c\x70\xc3\x80"
    b"\x18\x71\x83\xc0\x30\x71\x03\xc0\x60\x74\x01\x90"
    b"\x0c\x0e\x38\x38\x0f\xff\x3f\xfc\x0e\x0f\x38\x3c"
    b"\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c\x0f\xff\x38\x3c"
    b"\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c"
    b"\x0e\x0f\x38\x3c\x0f\xff\x38\x3c\x0e\x0e\x38\x3c"
    b"\x0e\x20\x38\x3c\x0e\x38\x38\x3c\x0e\x1c\x38\xf8"
    b"\x0e\x1e\x38\x78\x1f\xff\x38\x78\x7f\xc7\x38\x60"
    b"\x7f\x07\x38\x00\x3c\x07\x38\x00\x20\x00\x38\x00"
    b"\x00\x00\x30\x00\x00\x00\x00\x00"
)

CHARS = {
    "花": (FONT_82B1, 32, 32),
    "火": (FONT_706B, 32, 32),
    "節": (FONT_7BC0, 32, 32),
}


def glyph_pixel(data, width, x, y):
    row_bytes = (width + 7) // 8
    value = data[y * row_bytes + (x // 8)]
    return (value >> (7 - (x % 8))) & 1


def draw_char(display, char, x, y, shrink=1, wrap_y=False):
    if char not in CHARS:
        return
    data, w, h = CHARS[char]
    out_w = (w + shrink - 1) // shrink
    out_h = (h + shrink - 1) // shrink

    for oy in range(out_h):
        sy = oy * shrink
        for ox in range(out_w):
            sx = ox * shrink
            if sx < w and sy < h and glyph_pixel(data, w, sx, sy):
                px = x + ox
                py = y + oy
                if wrap_y:
                    py %= OLED_HEIGHT
                if 0 <= px < OLED_WIDTH and 0 <= py < OLED_HEIGHT:
                    display.pixel(px, py, 1)


def read_sensor_safe(sensor_obj):
    try:
        sensor_obj.measure()
        temp_c = sensor_obj.temperature()
        humidity = sensor_obj.humidity()
        print("[DEBUG] temperature={:.1f}C humidity={:.1f}%".format(temp_c, humidity))
        return temp_c, humidity, None
    except Exception as e:
        print("[ERROR] temperature/humidity read failed:", e)
        return None, None, str(e)


def draw_static_scene(display):
    display.fill(0)
    draw_tiny_text(display, "PENGHU UNIVERSITY", 2, ty(2))
    draw_tiny_text(display, "OF SCIENCE", 2, ty(10))
    draw_tiny_text(display, "AND TECHNOLOGY", 2, ty(18))
    draw_tiny_text(display, "ID:1114405056", 2, ty(26))

    draw_circle(display, dragon_x(), dragon_y(), 35, 1)
    draw_circle(display, dragon_x(), dragon_y(), 32, 1)


def draw_chinese_animation(display, frame):
    chars = "花火節"
    base_y = 78
    base_x = 104
    spacing = 4
    wave = (-4, 0, 4, 0)
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

        draw_char(display, ch, x, y, shrink=shrink, wrap_y=True)
        cy += size + spacing


def draw_temperature(display, temp_c, humidity, sensor_error):
    if temp_c is None:
        temp_text = "--.-C"
    else:
        temp_text = "{:.1f}C".format(temp_c)

    if humidity is None:
        rh_text = "RH ---%"
    else:
        rh_text = "RH {}%".format(int(humidity + 0.5))

    star_size = 10
    if temp_c is not None:
        if temp_c >= 32:
            star_size = 13
        elif temp_c >= 28:
            star_size = 11
        else:
            star_size = 9

    # Draw star first so the sensor box remains readable on top.
    draw_star(display, dragon_x(), dragon_y(), star_size, 1)

    # SH1107 rotate=90 safe margins near right/bottom edges.
    box_w = 54
    box_h = 24
    right_margin = 32
    bottom_margin = 16
    box_x = OLED_WIDTH - right_margin - box_w
    box_y = OLED_HEIGHT - bottom_margin - box_h

    display.fill_rect(box_x + 1, box_y + 1, box_w - 2, box_h - 2, 0)
    display.rect(box_x, box_y, box_w, box_h, 1)

    temp_width = len(temp_text) * 4
    rh_width = len(rh_text) * 4

    temp_x = box_x + (box_w - temp_width) // 2
    rh_x = box_x + (box_w - rh_width) // 2

    draw_tiny_text(display, temp_text, temp_x, box_y + 3)
    draw_tiny_text(display, rh_text, rh_x, box_y + 13)

    if sensor_error:
        draw_tiny_text(display, "ERR", box_x + 2, box_y + 13)


last_temp = None
last_humidity = None
sensor_error = False

frame = 0
last_sensor_ms = time.ticks_ms() - SENSOR_INTERVAL_MS

while True:
    now_ms = time.ticks_ms()
    if time.ticks_diff(now_ms, last_sensor_ms) >= SENSOR_INTERVAL_MS:
        t, h, err = read_sensor_safe(sensor)
        if t is not None and h is not None:
            last_temp = t
            last_humidity = h
            sensor_error = False
        else:
            sensor_error = True
        last_sensor_ms = now_ms

    draw_static_scene(oled)
    draw_chinese_animation(oled, frame)
    draw_temperature(oled, last_temp, last_humidity, sensor_error)
    oled.show()

    frame = (frame + 1) % 12
    time.sleep_ms(ANIM_INTERVAL_MS)
