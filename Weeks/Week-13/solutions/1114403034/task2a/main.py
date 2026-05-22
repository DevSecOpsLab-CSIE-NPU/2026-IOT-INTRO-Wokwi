from machine import Pin, I2C
import ssd1306
import framebuf
import math
import time

# ESP32 I2C pin assignment for SSD1306

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

FONT_3X5 = {
    'A': ('111', '101', '111', '101', '101'),
    'C': ('111', '100', '100', '100', '111'),
    'D': ('110', '101', '101', '101', '110'),
    'E': ('111', '100', '110', '100', '111'),
    'F': ('111', '100', '110', '100', '100'),
    'G': ('111', '100', '101', '101', '111'),
    'H': ('101', '101', '111', '101', '101'),
    'I': ('111', '010', '010', '010', '111'),
    'L': ('100', '100', '100', '100', '111'),
    'N': ('101', '111', '111', '111', '101'),
    'O': ('111', '101', '101', '101', '111'),
    'P': ('111', '101', '111', '100', '100'),
    'R': ('111', '101', '111', '110', '101'),
    'S': ('111', '100', '111', '001', '111'),
    'T': ('111', '010', '010', '010', '010'),
    'U': ('101', '101', '101', '101', '111'),
    'V': ('101', '101', '101', '101', '010'),
    'Y': ('101', '101', '010', '010', '010'),
    '0': ('111', '101', '101', '101', '111'),
    '2': ('111', '001', '111', '100', '111'),
    '6': ('111', '100', '111', '101', '111'),
    ' ': ('000', '000', '000', '000', '000'),
    '?': ('111', '001', '011', '000', '010'),
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
    '?': (FONT_82B1, 32, 32),
    '!': (FONT_706B, 32, 32),
    '#': (FONT_7BC0, 32, 32),
}


def draw_tiny_text(display, text, x, y, color=1):
    cursor_x = x
    for ch in text.upper():
        glyph = FONT_3X5.get(ch, FONT_3X5['?'])
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == '1':
                    display.pixel(cursor_x + col, y + row, color)
        cursor_x += 4


def draw_tiny_char_scaled(display, ch, x, y, scale=1, color=1):
    glyph = FONT_3X5.get(ch.upper(), FONT_3X5['?'])
    for row, bits in enumerate(glyph):
        for col, bit in enumerate(bits):
            if bit == '1':
                display.fill_rect(x + col * scale, y + row * scale, scale, scale, color)


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


def draw_rotating_star(display, cx, cy, radius, angle, scale=1.0, color=1):
    pts = []
    for i in range(10):
        r = radius if (i % 2 == 0) else int(radius * 0.45)
        a = angle + i * math.pi / 5
        x = cx + int(math.sin(a) * r * scale)
        y = cy - int(math.cos(a) * r * scale)
        pts.append((x, y))
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        display.line(x1, y1, x2, y2, color)


def draw_orbit_sparks(display, cx, cy, radius, frame, color=1):
    for i in range(8):
        a = frame * 0.25 + i * math.pi / 4
        x = cx + int(math.cos(a) * radius)
        y = cy + int(math.sin(a) * radius)
        display.pixel(x, y, color)
        display.pixel(x + 1, y, color)
        display.pixel(x, y + 1, color)


def draw_tiny_text_wave(display, text, x, y, frame, spacing=1):
    cursor_x = x
    for i, ch in enumerate(text.upper()):
        phase = frame * 0.22 + i * 0.9
        offset = int(math.sin(phase) * 4)
        scale = 2 if math.sin(phase) > 0.25 else 1
        draw_tiny_char_scaled(display, ch, cursor_x, y + offset, scale)
        cursor_x += 4 * scale + spacing


def draw_char(oled, char, x, y, shrink=1):
    if char not in CHARS:
        return
    data, w, h = CHARS[char]
    fb = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
    if shrink <= 1:
        oled.blit(fb, x, y)
        return
    out_w = (w + shrink - 1) // shrink
    out_h = (h + shrink - 1) // shrink
    for oy in range(out_h):
        sy = oy * shrink
        for ox in range(out_w):
            sx = ox * shrink
            if fb.pixel(sx, sy):
                oled.pixel(x + ox, y + oy, 1)


def draw_text(oled, text, x, y, spacing=0, shrink=1):
    cx = x
    for ch in text:
        if ch in CHARS:
            _, w, _ = CHARS[ch]
            draw_char(oled, ch, cx, y, shrink=shrink)
            draw_w = (w + shrink - 1) // shrink
            cx += draw_w + spacing


def draw_text_vertical(oled, text, x, y, spacing=0, shrink=1):
    cy = y
    for ch in text:
        if ch in CHARS:
            _, _, h = CHARS[ch]
            draw_char(oled, ch, x, cy, shrink=shrink)
            draw_h = (h + shrink - 1) // shrink
            cy += draw_h + spacing


def draw_text_vertical_flash(oled, text, x, y, frame, spacing=0, shrink=1):
    cy = y
    for idx, ch in enumerate(text):
        if ch not in CHARS:
            cy += 12 + spacing
            continue
        phase = (frame + idx * 7) % 24
        if phase < 17:
            dx = int(math.sin(frame * 0.18 + idx) * 2)
            dy = int(math.sin(frame * 0.13 + idx) * 1)
            draw_char(oled, ch, x + dx, cy + dy, shrink=shrink)
            if phase < 5:
                draw_char(oled, ch, x + dx + 1, cy + dy, shrink=shrink)
        cy += (32 + shrink - 1) // shrink + spacing


def draw_left_info(display, frame):
    draw_tiny_text(display, 'Penghu', 2, 2)
    draw_tiny_text(display, 'University', 2, 10)
    draw_tiny_text(display, 'Dept', 2, 24)
    draw_tiny_text(display, 'of', 12, 32)
    draw_tiny_text_wave(display, 'CSIE', 2, 40, frame)
    draw_tiny_text(display, 'of Science', 2, 52)
    draw_tiny_text(display, 'and Technology', 2, 58)


def render_frame(display, frame):
    display.fill(0)
    draw_left_info(display, frame)
    display.text('2026', 96, 2)
    draw_circle(display, 64, 32, 28)
    scale = 1.0 + 0.18 * math.sin(frame * 0.14)
    draw_rotating_star(display, 64, 32, 11, frame * 0.25, scale)
    draw_orbit_sparks(display, 64, 32, 26, frame)
    draw_text_vertical_flash(display, '?!#', 108, 12, frame, spacing=2, shrink=2)
    display.show()

frame = 0
while True:
    render_frame(oled, frame)
    time.sleep(0.06)
    frame += 1
