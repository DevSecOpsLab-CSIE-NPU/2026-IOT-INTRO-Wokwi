from machine import Pin, I2C
import ssd1306
import framebuf
import time
import math

# ESP32 I2C pin assignment for SSD1306

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

FONT_3X5 = {
    "A": ("111", "101", "111", "101", "101"),
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
    "2": ("111", "001", "111", "100", "111"),
    "6": ("111", "100", "111", "101", "111"),
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
    '花': (FONT_82B1, 32, 32),
    '火': (FONT_706B, 32, 32),
    '節': (FONT_7BC0, 32, 32),
}


def draw_tiny_char(display, ch, x, y, scale=1, color=1):
    glyph = FONT_3X5.get(ch, FONT_3X5["?"])
    for row, bits in enumerate(glyph):
        for col, bit in enumerate(bits):
            if bit == "1":
                for sy in range(scale):
                    for sx in range(scale):
                        display.pixel(x + col * scale + sx, y + row * scale + sy, color)


def draw_tiny_text(display, text, x, y, scale=1, color=1):
    cursor_x = x
    for ch in text.upper():
        draw_tiny_char(display, ch, cursor_x, y, scale=scale, color=color)
        cursor_x += 4 * scale


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


def draw_rotating_star(display, cx, cy, outer_radius, inner_radius, angle, color=1):
    pts = []
    for i in range(10):
        radius = outer_radius if (i % 2) == 0 else inner_radius
        theta = angle + i * math.pi / 5
        pts.append((cx + int(radius * math.cos(theta)), cy + int(radius * math.sin(theta))))
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        display.line(x1, y1, x2, y2, color)


def draw_orbit_sparks(display, cx, cy, radius, angle, color=1):
    for i in range(8):
        theta = angle + i * math.pi / 4
        px = cx + int(radius * math.cos(theta))
        py = cy + int(radius * math.sin(theta))
        display.pixel(px, py, color)
        if i % 2 == 0:
            display.pixel(px, py - 1, color)
            display.pixel(px, py + 1, color)


def glyph_pixel(data, width, x, y):
    row_bytes = (width + 7) // 8
    value = data[y * row_bytes + x // 8]
    return (value >> (7 - (x % 8))) & 1


def draw_char(display, char, x, y, shrink=1):
    if char not in CHARS:
        return
    data, w, h = CHARS[char]
    if shrink <= 1:
        fb = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
        display.blit(fb, x, y)
        return
    out_w = (w + shrink - 1) // shrink
    out_h = (h + shrink - 1) // shrink
    for oy in range(out_h):
        sy = oy * shrink
        for ox in range(out_w):
            sx = ox * shrink
            if glyph_pixel(data, w, sx, sy):
                display.pixel(x + ox, y + oy, 1)


def draw_text_vertical(display, text, x, y, spacing=0, shrink=1):
    cy = y
    for ch in text:
        if ch in CHARS:
            _, _, h = CHARS[ch]
            draw_char(display, ch, x, cy, shrink=shrink)
            cy += (h + shrink - 1) // shrink + spacing


def draw_text_vertical_flash(display, text, x, y, frame):
    active = frame % len(text)
    cy = y
    for idx, ch in enumerate(text):
        draw_char(display, ch, x, cy, shrink=2)
        if idx == active:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                px = x + dx + 8
                py = cy + dy + 8
                if 0 <= px < oled_width and 0 <= py < oled_height:
                    display.pixel(px, py, 1)
        cy += 16 + 4


def draw_tiny_text_wave(display, text, x, y, frame):
    wave = (-2, -1, 0, 1)
    active = frame % len(text)
    cursor_x = x
    for idx, ch in enumerate(text.upper()):
        scale = 2 if idx == active else 1
        offset = wave[(frame + idx) % len(wave)] - (1 if scale == 2 else 0)
        draw_tiny_char(display, ch, cursor_x, y + offset, scale=scale)
        cursor_x += 4 * scale


def draw_static_scene(display, angle):
    display.fill(0)
    draw_circle(display, 64, 32, 28)
    draw_circle(display, 64, 32, 24)
    draw_rotating_star(display, 64, 32, 14, 6, angle)
    draw_rotating_star(display, 64, 32, 10, 4, -angle)
    draw_orbit_sparks(display, 64, 32, 26, angle)
    draw_tiny_text(display, "PENGHU", 2, 2, scale=1)
    draw_tiny_text(display, "UNIVERSITY", 2, 10, scale=1)
    draw_tiny_text(display, "DEPT OF", 2, 22, scale=1)
    draw_tiny_text(display, "CSIE", 2, 30, scale=1)
    draw_tiny_text(display, "OF SCIENCE", 2, 42, scale=1)
    draw_tiny_text(display, "TECH", 2, 50, scale=1)
    display.text("2026", 96, 2, 1)


frame = 0
while True:
    angle = frame * 0.35
    draw_static_scene(oled, angle)
    draw_tiny_text_wave(oled, "CSIE", 80, 20, frame)
    draw_text_vertical_flash(oled, "花火節", 108, 6, frame)
    oled.show()
    frame += 1
    time.sleep_ms(120)
