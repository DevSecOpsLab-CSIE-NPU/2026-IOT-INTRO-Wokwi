from machine import Pin, I2C
import framebuf
import sh1107
import dht
import time

# ===== Hardware setup =====
i2c = I2C(0, scl=Pin(21), sda=Pin(22))
oled = sh1107.SH1107_I2C(128, 128, i2c, address=0x3C, rotate=90)
dht_sensor = dht.DHT22(Pin(23))

# ===== Tunable constants =====
CENTER_X = 64
CENTER_Y = 64
DRAGON_CENTER_X = CENTER_X - 32
DRAGON_CENTER_Y = CENTER_Y
FRAME_INTERVAL_MS = 250
SENSOR_INTERVAL_MS = 2000
CHINESE_BASE_X = 97
CHINESE_BASE_Y = 10
CHINESE_SPACING = 3

# ===== Chinese glyph data (32x32) =====
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
    points = [
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
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        display.line(x1, y1, x2, y2, color)


def draw_char(display, char, x, y, shrink=1, wrap_y=False):
    item = CHARS.get(char)
    if item is None:
        return

    data, width, height = item
    fb = framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)

    if shrink <= 1:
        for sy in range(height):
            py = y + sy
            if wrap_y:
                py %= 128
            if py < 0 or py >= 128:
                continue
            for sx in range(width):
                if fb.pixel(sx, sy):
                    px = x + sx
                    if 0 <= px < 128:
                        display.pixel(px, py, 1)
        return

    out_w = (width + shrink - 1) // shrink
    out_h = (height + shrink - 1) // shrink
    for oy in range(out_h):
        sy = oy * shrink
        py = y + oy
        if wrap_y:
            py %= 128
        if py < 0 or py >= 128:
            continue
        for ox in range(out_w):
            sx = ox * shrink
            if fb.pixel(sx, sy):
                px = x + ox
                if 0 <= px < 128:
                    display.pixel(px, py, 1)


def draw_static_scene(display):
    display.fill(0)

    # Header block
    display.text("Penghu University", 2, 2)
    display.text("of Science & Tech", 2, 12)
    display.text("Dept of CSIE", 2, 22)
    display.text("2026", 96, 2)

    # Student ID must be visible on OLED
    display.text("ID:1114405001", 2, 34)

    # Dragon ball visual
    draw_circle(display, DRAGON_CENTER_X, DRAGON_CENTER_Y, 21, 1)
    draw_circle(display, DRAGON_CENTER_X, DRAGON_CENTER_Y, 18, 1)
    draw_star(display, DRAGON_CENTER_X, DRAGON_CENTER_Y, 7, 1)

    # Temperature panel frame
    display.rect(2, 100, 88, 24, 1)
    display.text("TEMP", 6, 104)


def draw_chinese_animation(display, frame):
    chars = "花火節"
    active = frame % len(chars)
    wave = (-4, 0, 4, 0)
    y_cursor = CHINESE_BASE_Y

    for i, ch in enumerate(chars):
        enlarged = i == active
        shrink = 1 if enlarged else 2
        size = 32 if enlarged else 16
        x = CHINESE_BASE_X - 8 if enlarged else CHINESE_BASE_X
        y = y_cursor + wave[(frame + i) % len(wave)]
        if enlarged:
            y -= 8

        draw_char(display, ch, x, y, shrink=shrink, wrap_y=True)
        y_cursor += size + CHINESE_SPACING


def draw_temperature(display, temperature):
    display.fill_rect(6, 112, 80, 10, 0)
    if temperature is None:
        display.text("--.- C", 6, 112)
    else:
        display.text("{:.1f} C".format(temperature), 6, 112)


def draw_sensor_error(display):
    display.fill_rect(92, 100, 34, 24, 0)
    display.rect(92, 100, 34, 24, 1)
    display.text("Sensor", 94, 104)
    display.text("Error", 96, 114)


def clear_sensor_error(display):
    display.fill_rect(92, 100, 34, 24, 0)


def read_sensor_safe(last_temp, last_humidity):
    try:
        dht_sensor.measure()
        temp_c = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        print(
            "[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%".format(
                temp_c, humidity
            )
        )
        return temp_c, humidity, False
    except Exception as error:
        print("[ERROR] DHT22 read failed:", error)
        return last_temp, last_humidity, True


def main():
    frame = 0
    last_temp = None
    last_humidity = None
    sensor_error = False
    last_sensor_ms = time.ticks_ms() - SENSOR_INTERVAL_MS

    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, last_sensor_ms) >= SENSOR_INTERVAL_MS:
            last_temp, last_humidity, sensor_error = read_sensor_safe(
                last_temp, last_humidity
            )
            last_sensor_ms = now

        draw_static_scene(oled)
        draw_chinese_animation(oled, frame)
        draw_temperature(oled, last_temp)

        if sensor_error:
            draw_sensor_error(oled)
        else:
            clear_sensor_error(oled)

        oled.show()
        frame = (frame + 1) % 120
        time.sleep_ms(FRAME_INTERVAL_MS)


main()
