from machine import Pin, I2C
import ssd1306
import time
import math
import framebuf

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

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


def draw_tiny_char_scaled(display, ch, x, y, scale=1):
	glyph = FONT_3X5.get(ch.upper(), FONT_3X5["?"])
	for row, bits in enumerate(glyph):
		for col, bit in enumerate(bits):
			if bit != "1":
				continue
			px = x + col * scale
			py = y + row * scale
			for dy in range(scale):
				for dx in range(scale):
					display.pixel(px + dx, py + dy, 1)


def draw_tiny_text(display, text, x, y):
	cx = x
	for ch in text.upper():
		draw_tiny_char_scaled(display, ch, cx, y, 1)
		cx += 4


def draw_tiny_text_wave(display, text, x, y, frame):
	cx = x
	for i, ch in enumerate(text.upper()):
		wave = int(2 * math.sin((frame + i * 3) * 0.35))
		scale = 2 if (frame + i) % 6 in (0, 1) else 1
		draw_tiny_char_scaled(display, ch, cx, y + wave, scale)
		cx += (3 * scale) + 2


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


def draw_rotating_star(display, cx, cy, size, angle, color=1):
	pts = []
	for i in range(10):
		radius = size if i % 2 == 0 else int(size * 0.42)
		theta = angle + (math.pi / 5) * i - (math.pi / 2)
		x = cx + int(radius * math.cos(theta))
		y = cy + int(radius * math.sin(theta))
		pts.append((x, y))
	for i in range(len(pts)):
		x1, y1 = pts[i]
		x2, y2 = pts[(i + 1) % len(pts)]
		display.line(x1, y1, x2, y2, color)


def draw_orbit_sparks(display, cx, cy, radius, angle, color=1):
	for i in range(6):
		a = angle + (2 * math.pi * i / 6)
		x = cx + int(radius * math.cos(a))
		y = cy + int(radius * math.sin(a))
		display.pixel(x, y, color)


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


def draw_char(display, ch, x, y, shrink=1):
	if ch not in CHARS:
		return
	data, w, h = CHARS[ch]
	fb = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
	if shrink <= 1:
		display.blit(fb, x, y)
		return

	out_w = (w + shrink - 1) // shrink
	out_h = (h + shrink - 1) // shrink
	for oy in range(out_h):
		sy = oy * shrink
		for ox in range(out_w):
			sx = ox * shrink
			if fb.pixel(sx, sy):
				display.pixel(x + ox, y + oy, 1)


def draw_text_vertical_flash(display, text, x, y, frame):
	active = frame % len(text)
	cy = y
	for i, ch in enumerate(text):
		enlarged = i == active
		shrink = 1 if enlarged else 2
		size = 32 if enlarged else 16
		px = x - 8 if enlarged else x
		py = cy - 8 if enlarged else cy
		draw_char(display, ch, px, py, shrink=shrink)
		cy += size + 2


def render_frame(frame):
	oled.fill(0)

	draw_tiny_text(oled, "Penghu University", 2, 2)
	draw_tiny_text(oled, "of Science and Technology", 2, 10)
	draw_tiny_text(oled, "Dept of", 2, 18)
	oled.text("2026", 96, 2)

	cx, cy = 64, 32
	draw_circle(oled, cx, cy, 28, 1)
	draw_circle(oled, cx, cy, 24, 1)
	breath = 8 + int(2 * math.sin(frame * 0.2))
	angle = frame * 0.22
	draw_rotating_star(oled, cx, cy, breath, angle, 1)
	draw_rotating_star(oled, cx, cy, max(4, breath - 3), -angle * 1.3, 1)
	draw_orbit_sparks(oled, cx, cy, 31, angle * 0.7, 1)

	draw_text_vertical_flash(oled, "花火節", 104, 8, frame)
	draw_tiny_text_wave(oled, "CSIE", 2, 50, frame)

	oled.show()


frame_idx = 0
while True:
	render_frame(frame_idx)
	frame_idx = (frame_idx + 1) % 120
	time.sleep_ms(120)