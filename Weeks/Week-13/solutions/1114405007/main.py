from machine import Pin, I2C
import sh1107
import dht
import time
import framebuf

# ESP32 I2C pin assignment for Grove SH1107 OLED (match diagram.json wiring)
i2c = I2C(0, scl=Pin(18), sda=Pin(19))

oled_width = 128
oled_height = 128
oled = sh1107.SH1107_I2C(oled_width, oled_height, i2c, address=0x3C, rotate=90)
center_x = 64
center_y = 64
offset_x = -32
offset_y = 0

# SH1107 visible center calibration (with rotate=90 on this panel)
dragon_center_x = center_x + offset_x
dragon_center_y = center_y + offset_y

FRAME_DELAY_MS = 250
SENSOR_INTERVAL_MS = 2000
STUDENT_ID = "1114405007"

# DHT22 data pin (match diagram.json wiring)
dht_sensor = dht.DHT22(Pin(22))

# Font: NotoSerifCJK-Bold.ttc, size 32x32
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


def draw_char(display, char, x, y, shrink=1, wrap_y=False):
    if char not in CHARS:
        return
    data, w, h = CHARS[char]
    fb = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)

    if shrink <= 1:
        for py in range(h):
            ty = y + py
            if wrap_y:
                ty %= oled_height
            if ty < 0 or ty >= oled_height:
                continue
            for px in range(w):
                if not fb.pixel(px, py):
                    continue
                tx = x + px
                if 0 <= tx < oled_width:
                    display.pixel(tx, ty, 1)
        return

    out_w = (w + shrink - 1) // shrink
    out_h = (h + shrink - 1) // shrink
    for oy in range(out_h):
        sy = oy * shrink
        ty = y + oy
        if wrap_y:
            ty %= oled_height
        if ty < 0 or ty >= oled_height:
            continue
        for ox in range(out_w):
            sx = ox * shrink
            if not fb.pixel(sx, sy):
                continue
            tx = x + ox
            if 0 <= tx < oled_width:
                display.pixel(tx, ty, 1)


def read_sensor_safe(prev_temp, prev_humidity):
    try:
        dht_sensor.measure()
        temp_c = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        print("[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%".format(temp_c, humidity))
        return temp_c, humidity, True
    except Exception as e:
        print("[ERROR] DHT22 read failed:", e)
        if prev_temp is not None and prev_humidity is not None:
            print(
                "[WARN] keep previous value: temperature = {:.1f}C, humidity = {:.1f}%".format(
                    prev_temp, prev_humidity
                )
            )
        return prev_temp, prev_humidity, False


def draw_static_scene(display):
    display.hline(0, 12, oled_width, 1)
    display.vline(88, 0, oled_height, 1)
    display.text("DRAGON BALL", 2, 2)
    display.text("PENGHU U.", 2, 18)
    display.text("CSIE", 2, 28)
    display.text("ID:07", 2, 38)
    display.text("2026", 92, 2)


def draw_dragon_ball(display, frame):
    pulse = (0, 1, 0, -1)
    radius = 20 + pulse[frame % len(pulse)]
    star_size = 8 + (1 if frame % 8 < 4 else 0)
    draw_circle(display, dragon_center_x, dragon_center_y, radius, 1)
    draw_star(display, dragon_center_x, dragon_center_y, star_size, 1)


def draw_fireworks_background(display, frame):
    # (cx, cy, max_radius, period, offset)
    fireworks = [
        (16, 16, 8, 20, 1),
        (44, 22, 10, 18, 4),
        (74, 18, 8, 22, 7),
        (104, 24, 12, 16, 0),
        (118, 52, 10, 18, 6),
        (92, 48, 8, 20, 9),
        (20, 74, 9, 17, 3),
        (52, 86, 10, 19, 11),
        (84, 96, 9, 21, 14),
        (112, 92, 11, 15, 5),
        (34, 112, 8, 16, 8),
        (96, 114, 7, 14, 12),
    ]
    dirs = (
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (-1, 1),
        (1, -1),
        (-1, -1),
    )

    for cx, cy, max_r, period, offset in fireworks:
        phase = (frame + offset) % period
        if phase == 0:
            # Launch spark at the center.
            if 0 <= cx < oled_width and 0 <= cy < oled_height:
                display.pixel(cx, cy, 1)
            continue

        radius = min(max_r, phase)
        for dx, dy in dirs:
            x = cx + dx * radius
            y = cy + dy * radius
            if 0 <= x < oled_width and 0 <= y < oled_height:
                display.pixel(x, y, 1)

        # A faint inner ring gives the burst a fuller look.
        if radius > 2:
            draw_circle(display, cx, cy, radius // 2, 1)

    # Add tiny twinkles over the whole panel so the background feels alive.
    for i in range(20):
        tx = (frame * 7 + i * 13) % oled_width
        ty = (frame * 5 + i * 17) % oled_height
        if (tx + ty + frame) % 3 == 0:
            display.pixel(tx, ty, 1)


def draw_chinese_animation(display, frame):
    chars = "花火節"
    right_edge = 126
    base_y = 54
    active_idx = (frame // 3) % len(chars)
    wave = (-8, -4, 0, 4, 8, 4, 0, -4)
    sway = (-2, -1, 0, 1, 2, 1, 0, -1)

    for idx, ch in enumerate(chars):
        shrink = 1 if idx == active_idx else 2
        char_w = 32 if shrink == 1 else 16
        char_h = 32 if shrink == 1 else 16
        y = base_y + idx * 20 + wave[(frame + idx * 2) % len(wave)]
        x = right_edge - char_w + sway[(frame + idx) % len(sway)]
        if shrink == 1:
            y -= 8

        # Keep Chinese glyphs inside the visible area to avoid wrap-around split.
        y = max(14, min(y, oled_height - char_h - 2))
        x = max(88, min(x, right_edge - char_w))
        draw_char(display, ch, x, y, shrink=shrink, wrap_y=False)


def draw_temperature(display, temp_c, humidity, sensor_ok):
    # Clear the telemetry area so fireworks won't visually cover the readings.
    display.fill_rect(0, 82, 86, 46, 0)
    display.rect(0, 82, 86, 46, 1)

    display.text("TEMP", 2, 84)
    display.text("HUM", 2, 104)

    if temp_c is None:
        temp_text = "--.- C"
    else:
        temp_text = "{:.1f} C".format(temp_c)

    if humidity is None:
        hum_text = "--.- %"
    else:
        hum_text = "{:.1f} %".format(humidity)

    display.text(temp_text, 2, 94)
    display.text(hum_text, 2, 114)

    if not sensor_ok:
        display.text("Sensor Error", 14, 72)


temp_c = None
humidity = None
sensor_ok = False
frame = 0
last_sensor_ms = time.ticks_ms() - SENSOR_INTERVAL_MS

while True:
    now_ms = time.ticks_ms()
    if time.ticks_diff(now_ms, last_sensor_ms) >= SENSOR_INTERVAL_MS:
        temp_c, humidity, sensor_ok = read_sensor_safe(temp_c, humidity)
        last_sensor_ms = now_ms

    oled.fill(0)
    draw_static_scene(oled)
    draw_fireworks_background(oled, frame)
    draw_dragon_ball(oled, frame)
    draw_chinese_animation(oled, frame)
    draw_temperature(oled, temp_c, humidity, sensor_ok)
    oled.show()

    frame += 1
    time.sleep_ms(FRAME_DELAY_MS)
