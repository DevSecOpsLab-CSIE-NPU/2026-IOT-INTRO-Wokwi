from machine import Pin, I2C
import framebuf
import time
import math

try:
	import ssd1306  # type: ignore
except ImportError:
	ssd1306 = None


class SSD1306_I2C_FALLBACK(framebuf.FrameBuffer):
	def __init__(self, width, height, i2c, addr=0x3C):
		self.width = width
		self.height = height
		self.i2c = i2c
		self.addr = addr
		self.pages = self.height // 8
		self.buf = bytearray(self.pages * self.width)
		super().__init__(self.buf, self.width, self.height, framebuf.MONO_VLSB)
		self._init_display()

	def _write_cmd(self, cmd):
		self.i2c.writeto(self.addr, bytearray((0x80, cmd)))

	def _write_data(self):
		self.i2c.writeto(self.addr, b"\x40" + self.buf)

	def _init_display(self):
		for cmd in (
			0xAE,
			0x20,
			0x00,
			0x40,
			0xA1,
			0xC8,
			0x81,
			0x7F,
			0xA6,
			0xA8,
			0x3F,
			0xD3,
			0x00,
			0xD5,
			0x80,
			0xD9,
			0xF1,
			0xDA,
			0x12,
			0xDB,
			0x30,
			0x8D,
			0x14,
			0xAF,
		):
			self._write_cmd(cmd)
		self.fill(0)
		self.show()

	def show(self):
		self._write_cmd(0x21)
		self._write_cmd(0)
		self._write_cmd(self.width - 1)
		self._write_cmd(0x22)
		self._write_cmd(0)
		self._write_cmd(self.pages - 1)
		self._write_data()


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


# 字型: NotoSerifCJK-Bold.ttc, 32x32
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


def draw_rotating_star(display, cx, cy, size, angle, color=1):
	outer = []
	inner = []
	for i in range(5):
		a = angle + i * (2 * math.pi / 5)
		outer.append((int(cx + size * math.cos(a)), int(cy + size * math.sin(a))))
		b = a + math.pi / 5
		inner_r = size * 0.42
		inner.append((int(cx + inner_r * math.cos(b)), int(cy + inner_r * math.sin(b))))

	for i in range(5):
		x1, y1 = outer[i]
		x2, y2 = inner[i]
		x3, y3 = outer[(i + 1) % 5]
		display.line(x1, y1, x2, y2, color)
		display.line(x2, y2, x3, y3, color)


def draw_orbit_sparks(display, cx, cy, radius, frame):
	for i in range(8):
		a = frame * 0.15 + i * (2 * math.pi / 8)
		x = int(cx + radius * math.cos(a))
		y = int(cy + radius * math.sin(a))
		display.pixel(x, y, 1)


def draw_tiny_char_scaled(display, ch, x, y, scale=1, color=1):
	glyph = FONT_3X5.get(ch.upper(), FONT_3X5["?"])
	for row, bits in enumerate(glyph):
		for col, bit in enumerate(bits):
			if bit != "1":
				continue
			if scale <= 1:
				display.pixel(x + col, y + row, color)
			else:
				display.fill_rect(x + col * scale, y + row * scale, scale, scale, color)


def draw_tiny_text(display, text, x, y, color=1):
	cx = x
	for ch in text:
		draw_tiny_char_scaled(display, ch, cx, y, 1, color)
		cx += 4


def draw_tiny_text_wave(display, text, x, y, frame):
	cx = x
	for i, ch in enumerate(text):
		phase = frame * 0.32 + i * 0.9
		scale = 1 if math.sin(phase) < 0 else 2
		yoff = int(2 * math.sin(phase + 1.2))
		draw_tiny_char_scaled(display, ch, cx, y + yoff, scale, 1)
		cx += 4 if scale == 1 else 8


def draw_char(display, char, x, y, shrink=1):
	if char not in CHARS:
		return
	data, w, h = CHARS[char]
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


def draw_text_vertical_flash(display, text, x, y, frame, spacing=0, shrink=2):
	cy = y
	for i, ch in enumerate(text):
		_, _, h = CHARS[ch]
		visible = ((frame // 5 + i) % 3) != 0
		if visible:
			draw_char(display, ch, x, cy, shrink)
		cy += ((h + shrink - 1) // shrink) + spacing


def render_frame(display, frame):
	display.fill(0)

	# Left text area
	draw_tiny_text(display, "PENGHU", 2, 2)
	draw_tiny_text(display, "UNIVERSITY", 2, 10)
	draw_tiny_text(display, "DEPT", 2, 24)
	draw_tiny_text(display, "OF", 12, 32)
	draw_tiny_text_wave(display, "CSIE", 2, 40, frame)
	draw_tiny_text(display, "OF SCIENCE", 2, 52)

	# Dragon ball circle + animated star
	cx = 64
	cy = 32
	draw_circle(display, cx, cy, 28, 1)
	breath = int(2 * (1 + math.sin(frame * 0.18)))
	star_size = 8 + breath
	angle = frame * 0.22
	draw_rotating_star(display, cx, cy, star_size, angle)
	draw_rotating_star(display, cx, cy, int(star_size * 0.65), -angle * 1.2)
	draw_orbit_sparks(display, cx, cy, 22, frame)

	display.text("2026", 96, 2)
	draw_text_vertical_flash(display, "花火節", 100, 12, frame, spacing=1, shrink=2)

	display.show()


# ESP32 I2C pin assignment for SSD1306
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
if ssd1306 is not None:
	oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
else:
	oled = SSD1306_I2C_FALLBACK(oled_width, oled_height, i2c)

frame_idx = 0
while True:
	render_frame(oled, frame_idx)
	frame_idx += 1
	time.sleep(0.08)