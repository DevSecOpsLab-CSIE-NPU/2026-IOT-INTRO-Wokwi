from PIL import Image, ImageDraw, ImageFont
import math
import re
import sys
from pathlib import Path

W = 128
H = 128

# tiny 3x5 font (subset) for small labels
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
    "1": ("010","010","010","010","010"),
    "3": ("111","001","111","001","111"),
    "4": ("101","101","111","001","001"),
    "5": ("111","100","111","001","111"),
    "7": ("111","001","001","001","001"),
    "8": ("111","101","111","101","111"),
    "9": ("111","101","111","001","001"),
    ".": ("000","000","000","000","010"),
    " ": ("000","000","000","000","000"),
    "?": ("111","001","011","000","010"),
}

# Chinese glyphs copied from main.py (MONO_HLSB layout)
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


def fb_pixel_mono_hlsb(data, w, h, x, y):
    # MONO_HLSB horizontal bytes: each byte holds 8 horizontal pixels (LSB leftmost)
    # layout: rows of (w/8) bytes; index = y*(w//8) + x//8
    if x < 0 or x >= w or y < 0 or y >= h:
        return 0
    bytes_per_row = w // 8
    index = y * bytes_per_row + (x // 8)
    b = data[index]
    bit = (b >> (x % 8)) & 1
    return bit


def draw_char_to_image(img, ch, x, y, shrink=1, wrap_y=False):
    if ch not in CHARS:
        return
    data, w, h = CHARS[ch]
    for sy in range(0, h, shrink):
        for sx in range(0, w, shrink):
            if fb_pixel_mono_hlsb(data, w, h, sx, sy):
                px = x + sx // shrink
                py = y + sy // shrink
                if wrap_y:
                    py = py % H
                if 0 <= px < W and 0 <= py < H:
                    img.putpixel((px, py), 1)


def draw_tiny_text_to_image(img, text, x, y):
    cx = x
    for ch in text:
        glyph = FONT_3X5.get(ch, FONT_3X5.get(' '))
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == '1':
                    img.putpixel((cx + col, y + row), 1)
        cx += 4


def draw_circle(img, cx, cy, r):
    x = r
    y = 0
    err = 0
    while x >= y:
        for px, py in [(cx + x, cy + y),(cx + y, cy + x),(cx - y, cy + x),(cx - x, cy + y),(cx - x, cy - y),(cx - y, cy - x),(cx + y, cy - x),(cx + x, cy - y)]:
            if 0 <= px < W and 0 <= py < H:
                img.putpixel((px, py), 1)
        y += 1
        if err <= 0:
            err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1


def draw_star(img, cx, cy, size):
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
    # draw lines
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        draw_line(img, x1, y1, x2, y2)


def draw_line(img, x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx + dy
    while True:
        if 0 <= x1 < W and 0 <= y1 < H:
            img.putpixel((x1, y1), 1)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x1 += sx
        if e2 <= dx:
            err += dx
            y1 += sy


def draw_static_scene(img, temp_text=None):
    draw_circle(img, 64, 90, 35)
    draw_circle(img, 64, 90, 32)
    draw_star(img, 64, 90, 13)
    # tiny text lines
    draw_tiny_text_to_image(img, "Penghu University", 2, 38)
    draw_tiny_text_to_image(img, "of Science and Technology", 2, 46)
    draw_tiny_text_to_image(img, "Dept of CSIE", 2, 54)
    # year
    # use ImageDraw for ASCII numbers
    d = ImageDraw.Draw(img)
    d.text((96,38), "2026", fill=1)
    draw_tiny_text_to_image(img, "1114405021", 2, 70)
    if temp_text:
        d.text((40, 30), temp_text, fill=1)


def draw_dancing_chinese(img, frame):
    chars = "花火節"
    base_y = 78
    base_x = 104
    spacing = 4
    wave = (-5,0,5,0)
    active = frame % len(chars)
    cy = base_y
    for i, ch in enumerate(chars):
        enlarged = (i == active)
        shrink = 1 if enlarged else 2
        size = 32 if enlarged else 16
        x = base_x - 8 if enlarged else base_x
        y = cy + wave[(frame + i) % len(wave)]
        if enlarged:
            y -= 8
        draw_char_to_image(img, ch, x, y, shrink=shrink, wrap_y=True)
        cy += size + spacing


def render_frames(num_frames=20, fps=4):
    frames = []
    for f in range(num_frames):
        src = Image.new('1', (W, H), 0)
        # temp_text may be set by caller; we keep a global variable TEMP_TEXT
        draw_static_scene(src, temp_text=globals().get('TEMP_TEXT'))
        draw_dancing_chinese(src, f)
        # perform same blit_rotate as main.py (23 degrees CCW)
        dst = Image.new('1', (W, H), 0)
        angle = math.radians(23)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        cx = (W - 1) / 2.0
        cy = (H - 1) / 2.0
        src_pixels = src.load()
        dst_pixels = dst.load()
        for x in range(W):
            for y in range(H):
                if src_pixels[x, y]:
                    dx = x - cx
                    dy = y - cy
                    xr = cx + dx * cos_a - dy * sin_a
                    yr = cy + dx * sin_a + dy * cos_a
                    xi = int(round(xr))
                    yi = int(round(yr))
                    if 0 <= xi < W and 0 <= yi < H:
                        dst_pixels[xi, yi] = 1
        frames.append(dst)
    return frames

if __name__ == '__main__':
    # determine temperature text: CLI arg overrides file parsing
    TEMP_TEXT = None
    if len(sys.argv) > 1:
        # accept a single numeric temperature like 24.0 or a string
        try:
            t = float(sys.argv[1])
            TEMP_TEXT = '{:.1f} C'.format(t)
        except Exception:
            TEMP_TEXT = sys.argv[1]
    else:
        # try parse last temperature from esp32_dht/serial_capture.txt
        try:
            sc_path = Path(__file__).parent.parent / 'esp32_dht' / 'serial_capture.txt'
            if sc_path.exists():
                txt = sc_path.read_text(encoding='utf-8', errors='ignore')
                matches = re.findall(r"temperature\s*=\s*([0-9]+\.?[0-9]*)C", txt)
                if matches:
                    TEMP_TEXT = '{:.1f} C'.format(float(matches[-1]))
        except Exception:
            TEMP_TEXT = None

    frames = render_frames(num_frames=20, fps=4)
    # save first frame as PNG
    frames[0].save('../oled_screenshot.png')
    # save GIF ~5s (20 frames x 250ms = 5s)
    frames[0].save('../oled_5s.gif', save_all=True, append_images=frames[1:], duration=250, loop=0)
    print('Rendered ../oled_screenshot.png and ../oled_5s.gif')
