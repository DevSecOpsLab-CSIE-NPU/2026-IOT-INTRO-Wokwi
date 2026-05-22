from machine import Pin, I2C
import framebuf
import math
import time

import sh1107


i2c = I2C(0, scl=Pin(21), sda=Pin(22))
oled_width = 128
oled_height = 128
# rotate=0 是因為 diagram.json 已經把模組本體旋轉 270 度了，這裡不要再重複轉向。
oled = sh1107.SH1107_I2C(oled_width, oled_height, i2c, address=0x3C, rotate=0)


# 文字整體往下偏移的基準值；想讓左側英文/年份一起上下移時，主要改這裡。
TEXT_Y_OFFSET = 36


	# 所有左側靜態文字都會加上這個 y 偏移。
FONT_3X5 = {
	"A": ("111", "101", "111", "101", "101"),
	"C": ("111", "100", "100", "100", "111"),
	# scale 越大，字就越大；這裡只用在英文小字或 CSIE 放大效果。
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
	# angle 控制旋轉速度，breath 控制星星呼吸的放大縮小幅度。
	"Y": ("101", "101", "010", "010", "010"),
	"0": ("111", "101", "101", "101", "111"),
	"2": ("111", "001", "111", "100", "111"),
	"6": ("111", "100", "111", "101", "111"),
	" ": ("000", "000", "000", "000", "000"),
	# base_radius 越大，外圈火花離中心越遠；8 個火花會繞圈閃動。
	"?": ("111", "001", "011", "000", "010"),
}


def ty(value):
	return value + TEXT_Y_OFFSET


def draw_tiny_text(display, text, x, y, color=1):
	cursor_x = x
	for ch in text.upper():
		glyph = FONT_3X5.get(ch, FONT_3X5["?"])
		for row, bits in enumerate(glyph):
			for col, bit in enumerate(bits):
				if bit == "1":
	# shrink = 1 是原字大小，數字越大表示縮得越小。
	# wrap_y=True 時，超出底部的像素會接回上方，避免直排中文字被切掉。
					display.pixel(cursor_x + col, y + row, color)
		cursor_x += 4


def draw_tiny_text_scaled(display, text, x, y, scale=1, color=1):
	cursor_x = x
	for ch in text.upper():
		glyph = FONT_3X5.get(ch, FONT_3X5["?"])
	# 直排文字的 spacing 可以調整字與字之間的間距。
		for row, bits in enumerate(glyph):
			for col, bit in enumerate(bits):
				if bit == "1":
					px = cursor_x + col * scale
					py = y + row * scale
					for dy in range(scale):
						for dx in range(scale):
							display.pixel(px + dx, py + dy, color)
		cursor_x += 4 * scale
	# active_shrink / inactive_shrink 控制「放大」與「未放大」時的實際字體大小。
	# 數字越大字越小；如果覺得花火節太大，就把這兩個值再往上調。


def tiny_text_width(text, scale=1):
	return len(text) * 4 * scale


def draw_centered_tiny_text(display, text, y, scale=1, color=1):
	x = (oled_width - tiny_text_width(text, scale)) // 2
	draw_tiny_text_scaled(display, text, x, y, scale=scale, color=color)


def draw_circle(display, cx, cy, radius, color=1):
	x = radius
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


def star_points(cx, cy, outer_radius, inner_radius, angle):
	points = []
	for index in range(10):
		radius = outer_radius if index % 2 == 0 else inner_radius
	# 主視覺中心點；這兩個值最常拿來微調整顆龍珠的位置。
		theta = angle - math.pi / 2 + index * math.pi / 5
		x = cx + math.cos(theta) * radius
	# ring_radius 越大，外圈圓越大；可用來調整主球整體大小。
		y = cy + math.sin(theta) * radius
		points.append((int(round(x)), int(round(y))))
	return points


def draw_star(display, cx, cy, outer_radius, inner_radius, angle, color=1):
	points = star_points(cx, cy, outer_radius, inner_radius, angle)
	# CSIE 波浪字的位置；如果想更靠左或更靠下，可改這裡。
	for index in range(len(points)):
		x1, y1 = points[index]
		x2, y2 = points[(index + 1) % len(points)]
		display.line(x1, y1, x2, y2, color)


def draw_rotating_star(display, cx, cy, frame):
	angle = frame * 0.12
	breath = 0.5 + 0.5 * math.sin(frame * 0.18)
	# 星星本體也跟著縮小，避免只縮外圈看起來失衡。
	outer_radius = 10 + int(1 * breath)
	inner_radius = 4 + int(1 * breath)

	draw_star(display, cx, cy, outer_radius, inner_radius, angle, 1)


def draw_orbit_sparks(display, cx, cy, frame):
	# 外圈火花也一起往內縮，和主圓維持同一比例。
	base_radius = 20 + int(1 * math.sin(frame * 0.16))
	for index in range(8):
		angle = frame * 0.08 + index * (math.pi / 4)
		pulse = 1 + int((math.sin(frame * 0.25 + index) + 1) * 0.7)
		sx = int(round(cx + math.cos(angle) * base_radius))
		sy = int(round(cy + math.sin(angle) * (base_radius - 1)))
		ex = int(round(cx + math.cos(angle) * (base_radius + pulse)))
		ey = int(round(cy + math.sin(angle) * (base_radius + pulse)))
		display.line(sx, sy, ex, ey, 1)
		display.pixel(ex, ey, 1)


def draw_char(display, char, x, y, shrink=1, wrap_y=False):
	char = char.upper()
	glyph_data = CHARS.get(char)
	if glyph_data is None:
		return

	data, width, height = glyph_data
	fb = framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)
	if float(shrink) == 1.0 and not wrap_y:
		display.blit(fb, x, y)
		return

	out_w = int(math.ceil(width / float(shrink)))
	out_h = int(math.ceil(height / float(shrink)))
	for out_y in range(out_h):
		source_y = int(out_y * float(shrink))
		for out_x in range(out_w):
			source_x = int(out_x * float(shrink))
			if source_x < 0 or source_x >= width or source_y < 0 or source_y >= height:
				continue
			if fb.pixel(source_x, source_y):
				px = x + out_x
				py = y + out_y
				if wrap_y:
					py = py % oled_height
				if 0 <= px < oled_width and 0 <= py < oled_height:
					display.pixel(px, py, 1)


def draw_text(display, text, x, y, spacing=0, shrink=1):
	cursor_x = x
	for ch in text:
		if ch in CHARS:
			_, width, _ = CHARS[ch]
			draw_char(display, ch, cursor_x, y, shrink=shrink)
			step = int(math.ceil(width / float(shrink)))
			cursor_x += step + spacing


def draw_tiny_text_wave(display, text, x, y, frame):
	cursor_x = x
	for index, ch in enumerate(text):
		phase = frame * 0.45 + index * 1.05
		scale = 2 if math.sin(phase) > 0.15 else 1
		offset_y = int(round(math.sin(phase + math.pi / 2) * 3))
		draw_tiny_text_scaled(display, ch, cursor_x, y + offset_y, scale=scale)
		cursor_x += 4 * scale + 2


def draw_text_vertical(display, text, x, y, spacing=0, shrink=1):
	cursor_y = y
	for ch in text:
		if ch in CHARS:
			_, _, height = CHARS[ch]
			draw_char(display, ch, x, cursor_y, shrink=shrink)
			step = int(math.ceil(height / float(shrink)))
			cursor_y += step + spacing


def draw_text_vertical_flash(display, text, x, y, frame):
	cursor_y = y
	for index, ch in enumerate(text):
		phase = frame * 0.55 + index * 1.1
		active_shrink = 2.4
		inactive_shrink = 3.0
		shrink = active_shrink if math.sin(phase) > -0.05 else inactive_shrink
		wobble_x = int(round(math.sin(phase) * 1))
		wobble_y = int(round(math.cos(phase) * 2))
		draw_char(display, ch, x + wobble_x, cursor_y + wobble_y, shrink=shrink, wrap_y=True)
		if math.sin(phase) > 0.55:
			draw_char(display, ch, x + wobble_x + 1, cursor_y + wobble_y, shrink=shrink, wrap_y=True)
		height = CHARS[ch][2] if ch in CHARS else 5
		step = int(math.ceil(height / float(shrink)))
		cursor_y += step + 1


def draw_static_scene(display):
	display.fill(0)
	# 上方標題改成置中排版，字體也放大一級。
	draw_centered_tiny_text(display, "PENGHU", ty(4), scale=2)
	draw_centered_tiny_text(display, "UNIVERSITY", ty(18), scale=2)
	draw_centered_tiny_text(display, "DEPT OF", ty(32), scale=2)


def render_frame(display, frame):
	draw_static_scene(display)

	center_x = 64
	center_y = 96
	breathe = 0.5 + 0.5 * math.sin(frame * 0.12)
	# 主圓縮小一點，保留呼吸感但整體尺寸更精簡。
	ring_radius = 22 + int(1 * breathe)

	draw_circle(display, center_x, center_y, ring_radius, 1)
	draw_circle(display, center_x, center_y, ring_radius - 2, 1)
	draw_orbit_sparks(display, center_x, center_y, frame)
	draw_rotating_star(display, center_x, center_y, frame)

	draw_tiny_text_wave(display, "CSIE", 84, 114, frame)
	draw_text_vertical_flash(display, "花火節", 104, 78, frame)
	draw_tiny_text_scaled(display, "2026", 88, 118, scale=2)


CHARS = {
	"花": (
		bytearray(
			b"\x00\x00\x00\x00\x00\x7c\x1e\x00\x00\x78\x1c\x10"
			b"\x00\x78\x1c\x18\x00\x78\x1c\x3c\x7f\xff\xff\xfe"
			b"\x00\x78\x1c\x00\x00\x78\x1c\x00\x00\x78\x1c\x00"
			b"\x00\x00\x00\x00\x00\xf0\xf8\x00\x00\xf8\xf0\x00"
			b"\x01\xf0\xf0\x70\x01\xe0\xf0\xf8\x03\xc0\xf1\xf0"
			b"\x03\xc0\xf1\xe0\x07\xe0\xf3\xc0\x0f\xe0\xf7\x00"
			b"\x0d\xe0\xfc\x00\x19\xe0\xf0\x00\x31\xe0\xf0\x00"
			b"\x41\xe0\xf0\x00\x01\xe0\xf0\x04\x01\xe0\xf0\x04"
			b"\x01\xe0\xf0\x04\x01\xe0\xf0\x0c\x01\xe0\xf0\x0c"
			b"\x01\xe0\xff\xfe\x01\xe0\xff\xfe\x01\xe0\x7f\xfe"
			b"\x01\xc0\x0f\xe0\x00\x00\x00\x00"
		),
		32,
		32,
	),
	"火": (
		bytearray(
			b"\x00\x00\x00\x00\x00\x07\x00\x00\x00\x07\x80\x00"
			b"\x00\x07\x80\x00\x00\x07\x80\x00\x00\x07\x80\x00"
			b"\x00\x07\x80\x00\x01\x07\x80\x60\x01\x07\x80\xf0"
			b"\x01\x87\xc0\xfc\x01\x87\xc1\xf0\x03\x87\xc3\xe0"
			b"\x03\x87\xc3\xc0\x07\x8f\x47\x00\x0f\x8f\x6e\x00"
			b"\x1f\x0f\x68\x00\x1f\x0f\x30\x00\x1e\x0f\x30\x00"
			b"\x00\x1e\x30\x00\x00\x1e\x38\x00\x00\x1e\x1c\x00"
			b"\x00\x3c\x1e\x00\x00\x38\x1e\x00\x00\x78\x0f\x80"
			b"\x00\xf0\x0f\xc0\x01\xe0\x07\xf0\x03\xc0\x03\xfc"
			b"\x07\x00\x01\xfe\x0e\x00\x00\xf8\x18\x00\x00\x70"
			b"\x40\x00\x00\x10\x00\x00\x00\x00"
		),
		32,
		32,
	),
	"節": (
		bytearray(
			b"\x07\x80\x38\x00\x07\x84\x7c\x18\x07\x0e\x78\x3c"
			b"\x0f\xff\x7f\xfe\x0e\xe0\xe7\x00\x1c\x70\xc3\x80"
			b"\x18\x71\x83\xc0\x30\x71\x03\xc0\x60\x74\x01\x90"
			b"\x0c\x0e\x38\x38\x0f\xff\x3f\xfc\x0e\x0f\x38\x3c"
			b"\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c\x0f\xff\x38\x3c"
			b"\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c"
			b"\x0e\x0f\x38\x3c\x0f\xff\x38\x3c\x0e\x0e\x38\x3c"
			b"\x0e\x20\x38\x3c\x0e\x38\x38\x3c\x0e\x1c\x38\xf8"
			b"\x0e\x1e\x38\x78\x1f\xff\x38\x78\x7f\xc7\x38\x60"
			b"\x7f\x07\x38\x00\x3c\x07\x38\x00\x20\x00\x38\x00"
			b"\x00\x00\x30\x00\x00\x00\x00\x00"
		),
		32,
		32,
	),
	"?": (
		bytearray(
			b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
			b"\x00\x00\x00\x00\x00\x3f\xfc\x00\x00\x7f\xfe\x00"
			b"\x00\x70\x0e\x00\x00\x60\x06\x00\x00\x00\x06\x00"
			b"\x00\x00\x0c\x00\x00\x00\x18\x00\x00\x00\x30\x00"
			b"\x00\x00\x60\x00\x00\x00\xc0\x00\x00\x01\x80\x00"
			b"\x00\x03\x00\x00\x00\x06\x00\x00\x00\x0c\x00\x00"
			b"\x00\x0c\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00"
			b"\x00\x0c\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00"
			b"\x00\x0c\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00"
			b"\x00\x0c\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00"
			b"\x00\x00\x00\x00\x00\x00\x00\x00"
		),
		32,
		32,
	),
}


frame = 0
while True:
	render_frame(oled, frame)
	oled.show()
	frame += 1
	time.sleep(0.20)