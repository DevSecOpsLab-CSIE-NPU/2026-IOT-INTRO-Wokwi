
from machine import Pin, I2C
import ssd1306
import framebuf
import time
from math import sin, cos, pi

# 初始化 I2C 與 OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# 小字 3x5 點陣字型
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

def draw_tiny_text(display, text, x, y, scale=1, color=1):
	cx = x
	for ch in text.upper():
		glyph = FONT_3X5.get(ch, FONT_3X5['?'])
		for row, bits in enumerate(glyph):
			for col, bit in enumerate(bits):
				if bit == '1':
					if scale <= 1:
						display.pixel(cx + col, y + row, color)
					else:
						# 放大每個像素
						for sy in range(scale):
							for sx in range(scale):
								display.pixel(cx + col*scale + sx, y + row*scale + sy, color)
		cx += (3*scale) + scale

# 中文字型（從 task2 拷貝的 32x32 點陣）
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

def draw_text_vertical_flash(oled, text, x, y, frame_idx, shrink=2):
	# 逐字輪流高亮（簡單實作：持續顯示字型，閃爍由 frame_idx 控制）
	for i, ch in enumerate(text):
		on = ((frame_idx + i) // 4) % 2 == 0
		draw_char(oled, ch, x, y + i * ((32 + shrink - 1) // shrink + 2), shrink=shrink)
		if not on:
			# 畫黑色像素遮蓋來模擬 off（在 SSD1306 上以不畫白色達成）
			pass

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

def draw_rotating_star(display, cx, cy, angle, scale=1.0, color=1):
	pts = []
	outer = int(14 * scale)
	inner = int(6 * scale)
	for i in range(5):
		a_out = angle + i * 2 * pi / 5
		a_in = angle + (i + 0.5) * 2 * pi / 5
		pts.append((cx + int(cos(a_out) * outer), cy + int(sin(a_out) * outer)))
		pts.append((cx + int(cos(a_in) * inner), cy + int(sin(a_in) * inner)))
	for i in range(len(pts)):
		x1, y1 = pts[i]
		x2, y2 = pts[(i + 1) % len(pts)]
		display.line(x1, y1, x2, y2, color)

def draw_orbit_sparks(display, cx, cy, r, frame_idx):
	for i in range(8):
		a = frame_idx * 0.3 + i * (2 * pi / 8)
		x = cx + int(cos(a) * (r + 4))
		y = cy + int(sin(a) * (r + 4))
		if ((frame_idx + i) // 3) % 2 == 0:
			display.pixel(x, y, 1)

def draw_tiny_text_wave(display, text, x, y, frame_idx):
	for i, ch in enumerate(text.upper()):
		phase = frame_idx * 0.15 + i * 0.6
		scale = 1 + int((sin(phase) + 1) * 0.75)
		dy = int(sin(phase) * 4)
		draw_tiny_text(display, ch, x + i * 8, y + dy, scale=scale)

def draw_left_info_wave(display, lines, x, y, frame_idx):
	for i, line in enumerate(lines):
		phase = frame_idx * 0.12 + i * 0.45
		dy = int(sin(phase) * 1)
		dx = int(cos(phase) * 1)
		draw_tiny_text(display, line, x + dx, y + i * 7 + dy, scale=1)

def draw_text_vertical_flash(display, text, x, y, frame_idx, shrink=2):
	step = (32 + shrink - 1) // shrink + 2
	for i, ch in enumerate(text):
		phase = frame_idx * 0.18 + i * 0.7
		dy = int(sin(phase) * 2)
		# 輪流閃爍與微幅上下位移
		if ((frame_idx + i) // 3) % 2 == 0:
			draw_char(display, ch, x, y + i * step + dy, shrink=shrink)

def render_frame(frame_idx, angle):
	oled.fill(0)
	cx, cy = 78, 31
	# 調整版面：將主圖放在右半部，左側保留完整英文資訊區
	radius = 15
	draw_circle(oled, cx, cy, radius, 1)
	draw_orbit_sparks(oled, cx, cy, radius, frame_idx)
	breath = 1.0 + 0.18 * sin(frame_idx * 0.12)
	draw_rotating_star(oled, cx, cy, angle, scale=breath, color=1)

	# 左側英文小字資訊：完整保留並加上波浪位移
	draw_left_info_wave(oled, [
		"Penghu",
		"University",
		"Dept",
		"of",
		"CSIE",
		"of Science",
		"and Technology",
	], 2, 0, frame_idx)

	# CSIE 波浪舞（放在右上偏中位置，避免與主圖重疊）
	draw_tiny_text_wave(oled, "CSIE", 46, 4, frame_idx)

	# 右上角年份與直排中文字（保留原位）
	oled.text("2026", 96, 2)
	draw_text_vertical_flash(oled, "花火節", 104, 18, frame_idx, shrink=2)

	oled.show()

def main():
	frame = 0
	angle = 0.0
	try:
		while True:
			render_frame(frame, angle)
			frame += 1
			angle += 0.25
			time.sleep(0.06)
	except KeyboardInterrupt:
		pass

if __name__ == '__main__':
	main()