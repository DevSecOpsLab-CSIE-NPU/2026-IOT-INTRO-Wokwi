
from machine import Pin, I2C
import framebuf
import math
import time

import ssd1306


i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# 這份作業是 128x64 SSD1306，若換板子通常只要改這裡和接線腳位。


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
	draw_tiny_text_scaled(display, text, x, y, scale=1, color=color)


def draw_tiny_text_scaled(display, text, x, y, scale=2, color=1):
	cursor_x = x
	for ch in text.upper():
		glyph = FONT_3X5.get(ch, FONT_3X5["?"])
		for row, bits in enumerate(glyph):
			for col, bit in enumerate(bits):
				if bit == "1":
					px = cursor_x + col * scale
					py = y + row * scale
					for dy in range(scale):
						for dx in range(scale):
							display.pixel(px + dx, py + dy, color)
		cursor_x += 4 * scale


# 這個 3x5 小字型主要拿來畫左側資訊文字，也可以改成別的英文內容。


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
		theta = angle - math.pi / 2 + index * math.pi / 5
		x = cx + math.cos(theta) * radius
		y = cy + math.sin(theta) * radius
		points.append((int(round(x)), int(round(y))))
	return points


def draw_star(display, cx, cy, outer_radius, inner_radius, angle, color=1):
	points = star_points(cx, cy, outer_radius, inner_radius, angle)
	for index in range(len(points)):
		x1, y1 = points[index]
		x2, y2 = points[(index + 1) % len(points)]
		display.line(x1, y1, x2, y2, color)


def draw_rotating_star(display, cx, cy, frame):
	# angle 控制旋轉速度，breath 控制星星呼吸的放大縮小幅度。
	angle = frame * 0.12
	breath = 0.5 + 0.5 * math.sin(frame * 0.18)
	outer_radius = 8 + int(2 * breath)
	inner_radius = 4 + int(1 * breath)

	draw_star(display, cx, cy, outer_radius + 4, inner_radius + 3, angle, 1)
	draw_circle(display, cx, cy, outer_radius + 9, 1)


def draw_orbit_sparks(display, cx, cy, frame):
	# base_radius 決定火花離中心多遠，8 個點會繞圈閃動。
	base_radius = 18 + int(1 * math.sin(frame * 0.16))
	for index in range(8):
		angle = frame * 0.08 + index * (math.pi / 4)
		pulse = 1 + int((math.sin(frame * 0.25 + index) + 1) * 1.0)
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
	# 支援非整數 shrink（浮點），shrink == 1 表示原尺寸，>1 代表縮小，<1 代表放大
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


# shrink=1 是原字大小，shrink=2 會縮成一半；直排中文字就靠這個參數調整。


def draw_text(display, text, x, y, spacing=0, shrink=1):
	cursor_x = x
	for ch in text:
		if ch in CHARS:
			_, width, _ = CHARS[ch]
			draw_char(display, ch, cursor_x, y, shrink=shrink)
			step = int(math.ceil(width / float(shrink)))
			cursor_x += step + spacing


def draw_text_vertical(display, text, x, y, spacing=0, shrink=1):
	cursor_y = y
	for ch in text:
		if ch in CHARS:
			_, _, height = CHARS[ch]
			draw_char(display, ch, x, cursor_y, shrink=shrink)
			step = int(math.ceil(height / float(shrink)))
			cursor_y += step + spacing


def draw_tiny_text_wave(display, text, x, y, frame):
	# phase 會影響左右字的不同步感，scale 決定 CSIE 哪些字瞬間變大。
	cursor_x = x
	for index, ch in enumerate(text):
		phase = frame * 0.45 + index * 1.05
		scale = 2 if math.sin(phase) > 0.15 else 1
		offset_y = int(round(math.sin(phase + math.pi / 2) * 3))
		draw_tiny_text_scaled(display, ch, cursor_x, y + offset_y, scale=scale)
		cursor_x += 4 * scale + 2


def draw_text_vertical_flash(display, text, x, y, frame):
	# wobble_x / wobble_y 負責上下彈跳，亮一點的字會被重畫一次形成輪閃。
	cursor_y = y
	for index, ch in enumerate(text):
		phase = frame * 0.55 + index * 1.1
		# 調整放大與未放大時的縮放值，兩者都增大會讓字變得更小，但 active 仍稍微大於 inactive
		# shrink >1 表示放大後縮小比例（數值越大結果越小）：
		active_shrink = 2.0
		inactive_shrink = 2.6
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
	# 靜態背景每幀都重畫，避免上一幀殘影留在 OLED 上。
	display.fill(0)
	# 左側英文資訊：改為分行對齊參考圖
	draw_tiny_text(display, "PENGHU", 4, 4)
	draw_tiny_text(display, "UNIVERSITY", 4, 15)
	draw_tiny_text(display, "DEPT", 4, 26)
	draw_tiny_text(display, "OF", 9, 35)
	# CSIE 使用放大字（scale=2）放在左中段
	# 年份放到右上
	display.text("2026", 96, 4)


def render_frame(display, frame):
	draw_static_scene(display)

	# 主視覺中心往右移動以符合參考版面
	center_x = 72
	center_y = 32
	# breathe 越大，外圈圓和星星看起來越「鼓」；ring_radius 是外圈大小。
	breathe = 0.5 + 0.5 * math.sin(frame * 0.12)
	ring_radius = 28 + int(2 * breathe)

	draw_circle(display, center_x, center_y, ring_radius, 1)
	draw_circle(display, center_x, center_y, ring_radius - 8, 1)
	draw_orbit_sparks(display, center_x, center_y, frame)
	draw_rotating_star(display, center_x, center_y, frame)

	# CSIE 維持小幅波浪動畫（主體仍為靜態 CSIE）
	draw_tiny_text_wave(display, "CSIE", 6, 48, frame)
	# 直排花火節放在右側且縮小（shrink=2），啟用 wrap 以避免越線
	draw_text_vertical_flash(display, "花火節", 108, 12, frame)


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
	# 這裡就是幀率；數字越小動畫越快，太小會比較抖。
	time.sleep(0.20)