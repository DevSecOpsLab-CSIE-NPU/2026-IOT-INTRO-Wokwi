from machine import Pin, I2C
import dht
import framebuf
import sh1107
import time


i2c = I2C(0, scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 128
oled = sh1107.SH1107_I2C(oled_width, oled_height, i2c, address=0x3C, rotate=180)

center_x = 64
center_y = 90
dragon_center_x = center_x
dragon_center_y = center_y

FRAME_INTERVAL_MS = 170
SENSOR_INTERVAL_MS = 2000
STATUS_TOP = 96
STUDENT_ID = "ID: 48"

dht_sensor = dht.DHT22(Pin(23))

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
    "M": ("101", "111", "111", "101", "101"),
    "N": ("101", "111", "111", "111", "101"),
    "O": ("111", "101", "101", "101", "111"),
    "P": ("111", "101", "111", "100", "100"),
    "R": ("111", "101", "111", "110", "101"),
    "S": ("111", "100", "111", "001", "111"),
    "T": ("111", "010", "010", "010", "010"),
    "U": ("101", "101", "101", "101", "111"),
    "V": ("101", "101", "101", "101", "010"),
    "W": ("101", "101", "111", "111", "101"),
    "Y": ("101", "101", "010", "010", "010"),
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    ":": ("000", "010", "000", "010", "000"),
    "-": ("000", "000", "111", "000", "000"),
    " ": ("000", "000", "000", "000", "000"),
    "?": ("111", "001", "011", "000", "010"),
}


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
    "花": (FONT_82B1, 32, 32),
    "火": (FONT_706B, 32, 32),
    "節": (FONT_7BC0, 32, 32),
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
    for index in range(len(pts)):
        x1, y1 = pts[index]
        x2, y2 = pts[(index + 1) % len(pts)]
        display.line(x1, y1, x2, y2, color)


def draw_dragon_ball(display, cx, cy, radius, star_size, angle=0):
    draw_circle(display, cx, cy, radius, 1)
    draw_circle(display, cx, cy, radius - 2, 1)
    draw_star(display, cx, cy, star_size, 1)
    if angle == 1:
        display.line(cx - radius + 2, cy - 1, cx - radius + 7, cy - 2, 1)
        display.line(cx - radius + 2, cy + 1, cx - radius + 7, cy + 2, 1)
    elif angle == 2:
        display.line(cx + radius - 2, cy - 1, cx + radius - 7, cy - 2, 1)
        display.line(cx + radius - 2, cy + 1, cx + radius - 7, cy + 2, 1)


def draw_starfield(display, frame):
    seeds = [
        (8, 10), (16, 22), (28, 14), (42, 8), (58, 18), (76, 12), (94, 20), (112, 10),
        (10, 34), (22, 40), (36, 30), (52, 44), (68, 36), (84, 28), (100, 40), (116, 32),
        (6, 56), (18, 50), (30, 64), (46, 54), (62, 60), (78, 50), (96, 60), (118, 52),
        (14, 78), (28, 72), (40, 82), (58, 74), (72, 84), (90, 76), (108, 82), (120, 70),
    ]
    for index, (sx, sy) in enumerate(seeds):
        if (frame + index) % 6 == 0:
            display.pixel(sx, sy, 1)


def draw_dragon_balls(display, frame):
    balls = [
        (18, 118, 7, 3, 0),
        (36, 110, 8, 4, 1),
        (54, 116, 7, 3, 0),
        (70, 106, 8, 4, 2),
        (88, 116, 7, 3, 0),
        (104, 110, 8, 4, 1),
        (120, 118, 7, 3, 2),
    ]
    pulse = 1 if (frame % 4) < 2 else 0
    for cx, cy, radius, star_size, angle in balls:
        draw_circle(display, cx, cy, radius + pulse, 1)
        draw_circle(display, cx, cy, radius - 2 + pulse, 1)
        draw_star(display, cx, cy, star_size, 1)
        if angle == 0:
            display.line(cx - radius - 2, cy, cx - radius - 5, cy - 1, 1)
        elif angle == 1:
            display.line(cx + radius + 2, cy, cx + radius + 5, cy - 1, 1)
        else:
            display.line(cx, cy - radius - 2, cx + 1, cy - radius - 5, 1)


def draw_outline_body(display, points):
    for index in range(len(points) - 1):
        x1, y1 = points[index]
        x2, y2 = points[index + 1]
        display.line(x1, y1, x2, y2, 1)
        draw_circle(display, x1, y1, 3, 1)
        display.line(x1 + 1, y1, x2 + 1, y2, 1)


def draw_char(display, char, x, y, shrink=1, wrap_y=False):
    if char not in CHARS:
        return

    data, width, height = CHARS[char]
    fb = framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)

    if shrink <= 1:
        display.blit(fb, x, y)
        return

    out_w = (width + shrink - 1) // shrink
    out_h = (height + shrink - 1) // shrink
    for out_y in range(out_h):
        sample_y = out_y * shrink
        for out_x in range(out_w):
            sample_x = out_x * shrink
            if fb.pixel(sample_x, sample_y):
                pixel_x = x + out_x
                pixel_y = y + out_y
                if wrap_y:
                    pixel_y %= oled_height
                if 0 <= pixel_x < oled_width and 0 <= pixel_y < oled_height:
                    display.pixel(pixel_x, pixel_y, 1)


def draw_text_vertical(display, text, x, y, spacing=0, shrink=1, wrap_y=False):
    cursor_y = y
    for ch in text:
        if ch in CHARS:
            _, _, height = CHARS[ch]
            draw_char(display, ch, x, cursor_y, shrink=shrink, wrap_y=wrap_y)
            draw_h = (height + shrink - 1) // shrink
            cursor_y += draw_h + spacing


def read_sensor_safe():
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        print("[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%".format(temperature, humidity))
        return temperature, humidity, None
    except Exception as exc:
        print("[ERROR] DHT22 read failed:", exc)
        return None, None, exc


def draw_static_scene(display, frame):
    display.fill(0)
    pulse = frame % 4
    draw_circle(display, dragon_center_x, dragon_center_y, 35, 1)
    draw_circle(display, dragon_center_x, dragon_center_y, 32 + (pulse // 2), 1)
    draw_star(display, dragon_center_x, dragon_center_y, 13 + (pulse % 2), 1)

    draw_tiny_text(display, "Penghu University", 2, 2)
    draw_tiny_text(display, "of Science and Technology", 2, 10)
    draw_tiny_text(display, "Dept of CSIE", 2, 18)
    display.text("2026", 96, 2)

    display.line(0, 92, 127, 92, 1)
    display.line(96, 0, 96, 127, 1)


def draw_chinese_animation(display, frame):
    base_x = 100
    base_y = 38
    chars = "花火節"
    wave = [0, 2, 1, -1, -2, -1, 1, 2]
    for index, char in enumerate(chars):
        offset_y = wave[(frame + index) % len(wave)]
        offset_x = 1 if (frame + index) % 2 == 0 else 0
        if frame % 3 == 0:
            draw_char(display, char, base_x + offset_x + 1, base_y + index * 20 + offset_y + 1, shrink=2, wrap_y=True)
        draw_char(display, char, base_x + offset_x, base_y + index * 20 + offset_y, shrink=2, wrap_y=True)


def draw_shenron(display, frame):
    return


def draw_temperature_panel(display, temperature, humidity, sensor_error):
    display.line(0, STATUS_TOP, 127, STATUS_TOP, 1)
    display.text("TEMP", 2, 98)
    display.text("HUM", 2, 108)
    display.text("{:.1f} C".format(temperature), 36, 98)
    display.text("{:.0f}%".format(humidity), 36, 108)
    display.text(STUDENT_ID, 2, 116)
    if sensor_error:
        display.text("Sensor Error", 68, 98)


def draw_flash_effects(display, frame):
    aura_radii = [38, 41, 44]
    for index, radius in enumerate(aura_radii):
        if (frame + index) % 2 == 0:
            draw_circle(display, dragon_center_x, dragon_center_y, radius, 1)

    scan_y = 28 + ((frame * 4) % 56)
    if frame % 2 == 0:
        display.hline(0, scan_y, 96, 1)

    rays = [
        (0, -1),
        (1, -1),
        (1, 0),
        (1, 1),
        (0, 1),
        (-1, 1),
        (-1, 0),
        (-1, -1),
    ]
    base_length = 16 + (frame % 5)
    for index, (dx, dy) in enumerate(rays):
        if (frame + index) % 2 == 0:
            length = base_length + (index % 3)
            display.line(
                dragon_center_x,
                dragon_center_y,
                dragon_center_x + dx * length,
                dragon_center_y + dy * length,
                1,
            )

    spark_positions = [
        (-18, -4),
        (-12, -16),
        (2, -18),
        (16, -10),
        (18, 6),
        (10, 18),
        (-6, 18),
        (-18, 10),
    ]
    for index, (offset_x, offset_y) in enumerate(spark_positions):
        if (frame + index) % 3 != 0:
            spark_x = dragon_center_x + offset_x
            spark_y = dragon_center_y + offset_y
            display.pixel(spark_x, spark_y, 1)
            display.line(spark_x - 1, spark_y, spark_x + 1, spark_y, 1)
            display.line(spark_x, spark_y - 1, spark_x, spark_y + 1, 1)


def draw_status_equalizer(display, frame):
    base_x = 104
    bottom = 124
    for index in range(6):
        height = 5 + ((frame + index * 4) % 14)
        x = base_x + index * 4
        display.vline(x, bottom - height, height, 1)
        display.pixel(x - 1, bottom - height + 1, 1)
        display.pixel(x + 1, bottom - height + 1, 1)
        if (frame + index) % 2 == 0:
            display.pixel(x, bottom - height - 1, 1)


last_temperature = 0.0
last_humidity = 0.0
last_sensor_ok = False
last_sensor_ms = time.ticks_ms() - SENSOR_INTERVAL_MS
last_frame_ms = time.ticks_ms()
frame = 0

while True:
    now = time.ticks_ms()

    if time.ticks_diff(now, last_frame_ms) >= FRAME_INTERVAL_MS:
        frame = (frame + 1) % 64
        last_frame_ms = now

    sensor_error = False
    if time.ticks_diff(now, last_sensor_ms) >= SENSOR_INTERVAL_MS or not last_sensor_ok:
        temperature, humidity, error = read_sensor_safe()
        last_sensor_ms = now
        if error is None:
            last_temperature = temperature
            last_humidity = humidity
            last_sensor_ok = True
        else:
            sensor_error = True

    draw_static_scene(oled, frame)
    draw_flash_effects(oled, frame)
    draw_chinese_animation(oled, frame)
    draw_temperature_panel(oled, last_temperature, last_humidity, sensor_error)
    draw_status_equalizer(oled, frame)
    oled.show()
    time.sleep_ms(50)