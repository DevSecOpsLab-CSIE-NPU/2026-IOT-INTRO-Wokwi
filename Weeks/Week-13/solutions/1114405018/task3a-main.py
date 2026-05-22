from machine import Pin, I2C
import sh1107
import framebuf
import math
import time

# ESP32 I2C pin assignment for SH1107 (per task3a.md: scl=21, sda=22)
i2c = I2C(0, scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 128
# Use SH1107 driver at address 0x3C
oled = sh1107.SH1107_I2C(oled_width, oled_height, i2c, address=0x3C, rotate=0)

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


def draw_tiny_text(display, text, x, y, color=1):
    cursor_x = x
    for ch in text.upper():
        glyph = FONT_3X5.get(ch, FONT_3X5["?"])
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    display.pixel(cursor_x + col, y + row, color)
        cursor_x += 4


def draw_tiny_text_scaled(display, text, x, y, scale=1, color=1):
    cursor_x = x
    for ch in text.upper():
        glyph = FONT_3X5.get(ch, FONT_3X5["?"])
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    for sy in range(scale):
                        for sx in range(scale):
                            display.pixel(cursor_x + col * scale + sx, y + row * scale + sy, color)
        cursor_x += 4 * scale


def draw_tiny_text_variant(display, text, x, y, phase, color=1):
    cursor_x = x
    letters = text.upper()
    for index, ch in enumerate(letters):
        glyph = FONT_3X5.get(ch, FONT_3X5["?"])
        local = phase * len(letters) - index
        if local < 0:
            scale = 1
            dx = 0
            dy = 0
        elif local < 1:
            scale = 2 if local < 0.5 else 1
            dx = int(2 * local)
            dy = -int(1 * local)
        else:
            scale = 1
            dx = 0
            dy = 0

        draw_tiny_text_scaled(display, ch, cursor_x + dx, y + dy, scale=scale, color=color)
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


def draw_star(display, cx, cy, size, color=1):
    # Simple 5-point star for 128x64 OLED
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


def draw_rotated_star(display, cx, cy, size, angle, color=1):
    points = [
        (0, -size),
        (int(size * 0.35), -int(size * 0.25)),
        (size, -int(size * 0.2)),
        (int(size * 0.5), int(size * 0.25)),
        (int(size * 0.6), size),
        (0, int(size * 0.45)),
        (-int(size * 0.6), size),
        (-int(size * 0.5), int(size * 0.25)),
        (-size, -int(size * 0.2)),
        (-int(size * 0.35), -int(size * 0.25)),
    ]

    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    rotated = []
    for dx, dy in points:
        rx = int(dx * cos_a - dy * sin_a)
        ry = int(dx * sin_a + dy * cos_a)
        rotated.append((cx + rx, cy + ry))

    for i in range(len(rotated)):
        x1, y1 = rotated[i]
        x2, y2 = rotated[(i + 1) % len(rotated)]
        display.line(x1, y1, x2, y2, color)

# === 自動產生的中文點陣資料 ===
# 字型: NotoSerifCJK-Bold.ttc
# 大小: 32x32
# '花'  32x32
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

# '火'  32x32
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

# '節'  32x32
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

# 字 → bytearray 對照表
CHARS = {
    '花': (FONT_82B1, 32, 32),
    '火': (FONT_706B, 32, 32),
    '節': (FONT_7BC0, 32, 32),
}

def glyph_pixel(data, width, sx, sy):
    """Return pixel (0/1) from raw glyph bytearray using MSB-first bit order."""
    row_bytes = (width + 7) // 8
    idx = sy * row_bytes + (sx // 8)
    if idx < 0 or idx >= len(data):
        return 0
    value = data[idx]
    return (value >> (7 - (sx % 8))) & 1


def draw_char(oled, char, x, y, shrink=1, wrap_y=False):
    """Draw a Chinese glyph pixel-by-pixel, support shrink and wrap_y."""
    if char not in CHARS:
        return
    data, w, h = CHARS[char]
    out_w = (w + shrink - 1) // shrink
    out_h = (h + shrink - 1) // shrink

    for oy in range(out_h):
        sy = oy * shrink
        for ox in range(out_w):
            sx = ox * shrink
            if glyph_pixel(data, w, sx, sy):
                px = x + ox
                py = y + oy
                if wrap_y:
                    py %= oled_height
                if 0 <= px < oled_width and 0 <= py < oled_height:
                    oled.pixel(px, py, 1)

def draw_text(oled, text, x, y, spacing=0, shrink=1):
    """在 OLED 畫一串中文字，可用 shrink 縮小顯示"""
    cx = x
    for ch in text:
        if ch in CHARS:
            _, w, _ = CHARS[ch]
            draw_char(oled, ch, cx, y, shrink=shrink)
            draw_w = (w + shrink - 1) // shrink
            cx += draw_w + spacing


def draw_text_vertical(oled, text, x, y, spacing=0, shrink=1):
    """在 OLED 直排文字（由上到下）"""
    cy = y
    for ch in text:
        if ch in CHARS:
            _, _, h = CHARS[ch]
            draw_char(oled, ch, x, cy, shrink=shrink)
            draw_h = (h + shrink - 1) // shrink
            cy += draw_h + spacing


def draw_text_vertical_dynamic(oled, text, x, y, phase, spacing=1):
    """直排文字動畫：逐字放大，並加上波浪位移與滾動感"""
    if not text:
        return

    count = len(text)
    loop_pos = phase * count
    cy = y
    wave_phase = phase * math.tau * 2.0

    styles = [
        (0, 0, 1),
        (1, 0, 1),
        (0, 1, 1),
        (-1, 0, 1),
        (0, -1, 1),
        (1, 1, 2),
    ]

    def draw_styled_char(ch, px, py, shrink, style_id):
        sx, sy, repeat = styles[style_id % len(styles)]
        for offset in range(repeat):
            draw_char(oled, ch, px + sx * offset, py + sy * offset, shrink=shrink, wrap_y=True)

    for index, ch in enumerate(text):
        if ch not in CHARS:
            continue

        _, _, h = CHARS[ch]
        local = loop_pos - index
        style_id = index + int(phase * 6)

        if local < 0:
            shrink = 3
            offset_y = 0
        elif local < 1:
            if local < 0.25:
                shrink = 3
            elif local < 0.5:
                shrink = 2
            elif local < 0.75:
                shrink = 1
            else:
                shrink = 2
            offset_y = -int(3 * local)
        else:
            shrink = 3
            offset_y = 0

        wave_x = int(math.sin(wave_phase + index * 1.15) * (2 if shrink >= 2 else 3))
        wave_y = int(math.sin(wave_phase + index * 1.15 + (math.pi / 2)) * 1)

        if shrink <= 1:
            draw_h = h
        else:
            draw_h = (h + shrink - 1) // shrink

        draw_styled_char(ch, x + wave_x, cy + offset_y + wave_y, shrink, style_id)
        cy += draw_h + spacing


angle = 0.0
text_phase = 0.0
while True:
    # static scene parameters (task3a calibration)
    center_x = 64
    center_y = 90
    text_y_offset = 36

    def ty(y):
        return y + text_y_offset

    def draw_static_scene(display):
        display.fill(0)
        draw_circle(display, center_x, center_y, 35, 1)
        draw_circle(display, center_x, center_y, 32, 1)
        draw_star(display, center_x, center_y, 13, 1)
        draw_tiny_text(display, "Penghu University", 2, ty(2))
        draw_tiny_text(display, "of Science and Technology", 2, ty(10))
        draw_tiny_text(display, "Dept of CSIE", 2, ty(18))
        display.text("2026", 96, ty(2))

    draw_static_scene(oled)
    # draw dancing chinese at calibrated base coords
    draw_text_vertical_dynamic(oled, "花火節", 104, 78, text_phase, spacing=4)

    oled.show()
    angle += 0.12
    if angle >= math.tau:
        angle -= math.tau
    text_phase += 0.06
    if text_phase >= 1.0:
        text_phase -= 1.0
    time.sleep_ms(50)