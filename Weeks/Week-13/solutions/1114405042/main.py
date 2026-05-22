from machine import Pin, I2C
import time
import framebuf
import dht
import sh1107


OLED_WIDTH = 128
OLED_HEIGHT = 128
CENTER_X = 64
CENTER_Y = 90
TITLE_BOX_WIDTH = 88
TEMP_BOX_WIDTH = 88
CHINESE_X = 100
CHINESE_Y = 16
CHINESE_SPACING = 4
ANIMATION_FRAME_MS = 250
SENSOR_INTERVAL_MS = 2000


i2c = I2C(0, scl=Pin(21), sda=Pin(22))
oled = sh1107.SH1107_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, address=0x3C, rotate=0)
dht_sensor = dht.DHT22(Pin(23))


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
    for index in range(len(points)):
        x1, y1 = points[index]
        x2, y2 = points[(index + 1) % len(points)]
        display.line(x1, y1, x2, y2, color)


def glyph_pixel(data, width, x, y):
    row_bytes = (width + 7) // 8
    value = data[y * row_bytes + x // 8]
    return (value >> (7 - (x % 8))) & 1


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
        src_y = out_y * shrink
        for out_x in range(out_w):
            src_x = out_x * shrink
            if fb.pixel(src_x, src_y):
                pixel_x = x + out_x
                pixel_y = y + out_y
                if wrap_y:
                    pixel_y %= OLED_HEIGHT
                if 0 <= pixel_x < OLED_WIDTH and 0 <= pixel_y < OLED_HEIGHT:
                    display.pixel(pixel_x, pixel_y, 1)


def draw_static_scene(display, temp_text, show_error):
    display.fill(0)
    display.rect(0, 0, TITLE_BOX_WIDTH, 22, 1)
    display.rect(0, 26, TEMP_BOX_WIDTH, 28, 1)
    display.vline(92, 0, OLED_HEIGHT, 1)
    display.text("PENGHU", 4, 4)
    display.text("IOT LAB", 4, 14)
    display.text("2026", 96, 4)
    display.text("TEMP", 4, 32)
    display.text(temp_text, 4, 42)
    display.text("1114405042", 4, 56)
    if show_error:
        display.text("Sensor Error", 4, 70)
    draw_circle(display, CENTER_X, CENTER_Y, 35, 1)
    draw_circle(display, CENTER_X, CENTER_Y, 32, 1)
    draw_star(display, CENTER_X, CENTER_Y, 13, 1)


def draw_chinese_animation(display, frame):
    chars = "花火節"
    active_index = frame % len(chars)
    wave = (-4, 0, 4, 0)
    current_y = CHINESE_Y

    for index, char in enumerate(chars):
        enlarged = index == active_index
        shrink = 1 if enlarged else 2
        x = CHINESE_X - 8 if enlarged else CHINESE_X
        y = current_y + wave[(frame + index) % len(wave)]
        if enlarged:
            y -= 8
        draw_char(display, char, x, y, shrink=shrink, wrap_y=True)
        _, _, height = CHARS[char]
        current_y += (height + shrink - 1) // shrink + CHINESE_SPACING


def read_sensor_safe(previous_temp, previous_humidity):
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        print("[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%".format(temperature, humidity))
        return temperature, humidity, None
    except Exception as error:
        print("[ERROR] DHT22 read failed:", error)
        return previous_temp, previous_humidity, error


def format_temperature(value):
    if value is None:
        return "--.- C"
    return "{:.1f} C".format(value)


last_temperature = None
last_humidity = None
next_sensor_read = time.ticks_ms()
frame = 0

while True:
    now = time.ticks_ms()
    sensor_error = None
    if time.ticks_diff(now, next_sensor_read) >= 0:
        last_temperature, last_humidity, sensor_error = read_sensor_safe(
            last_temperature, last_humidity
        )
        next_sensor_read = time.ticks_add(now, SENSOR_INTERVAL_MS)

    temperature_text = format_temperature(last_temperature)
    draw_static_scene(oled, temperature_text, sensor_error is not None and last_temperature is None)
    draw_chinese_animation(oled, frame)
    oled.show()
    frame = (frame + 1) % 30000
    time.sleep_ms(ANIMATION_FRAME_MS)