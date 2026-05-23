from machine import Pin, I2C
import time
import math
import framebuf
import sh1107
import dht

# I2C for this task (scl=Pin(21), sda=Pin(22))
i2c = I2C(0, scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 128
# rotate left 90 degrees
oled = sh1107.SH1107_I2C(oled_width, oled_height, i2c, address=0x3C, rotate=0)

# DHT22 sensor on Pin 23
dht_sensor = dht.DHT22(Pin(23))

# off-screen source framebuffer for rotation rendering
src_buf = bytearray(oled_width * oled_height // 8)
src_fb = framebuf.FrameBuffer(src_buf, oled_width, oled_height, framebuf.MONO_HLSB)

# Student ID to show
STUDENT_ID = "1114405021"

# Debug: if True, skip rotation and directly blit src_fb to oled for testing
DEBUG_DIRECT_DRAW = True

# --- tiny 3x5 font for English small text ---
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


# --- circle and star drawing ---
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


# --- Chinese fonts (32x32) copied from task3a ---
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


def draw_char(oled, char, x, y, shrink=1, wrap_y=False):
	if char not in CHARS:
		return
	data, w, h = CHARS[char]
	fb = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
	if shrink <= 1:
		# blit may wrap; use try
		try:
			oled.blit(fb, x, y)
		except Exception:
			# fallback to pixel copy
			for sy in range(h):
				for sx in range(w):
					if fb.pixel(sx, sy):
						py = y + sy
						if wrap_y:
							py %= oled_height
						if 0 <= x + sx < oled_width and 0 <= py < oled_height:
							oled.pixel(x + sx, py, 1)
		return

	out_w = (w + shrink - 1) // shrink
	out_h = (h + shrink - 1) // shrink
	for oy in range(out_h):
		sy = oy * shrink
		for ox in range(out_w):
			sx = ox * shrink
			if fb.pixel(sx, sy):
				py = y + oy
				if wrap_y:
					py %= oled_height
				if 0 <= x + ox < oled_width and 0 <= py < oled_height:
					oled.pixel(x + ox, py, 1)


def draw_text_vertical(oled, text, x, y, spacing=0, shrink=1, wrap_y=False):
	cy = y
	for ch in text:
		if ch in CHARS:
			_, _, h = CHARS[ch]
			draw_char(oled, ch, x, cy, shrink=shrink, wrap_y=wrap_y)
			draw_h = (h + shrink - 1) // shrink
			cy += draw_h + spacing


# --- static scene and dancing chinese animation ---
center_x = 64
center_y = 90


def ty(y):
	return y + 36


def draw_static_scene(display, temp_text=None):
	display.fill(0)
	draw_circle(display, center_x, center_y, 35, 1)
	draw_circle(display, center_x, center_y, 32, 1)
	draw_star(display, center_x, center_y, 13, 1)
	draw_tiny_text(display, "Penghu University", 2, ty(2))
	draw_tiny_text(display, "of Science and Technology", 2, ty(10))
	draw_tiny_text(display, "Dept of CSIE", 2, ty(18))
	display.text("2026", 96, ty(2))
	# student id small label
	draw_tiny_text(display, STUDENT_ID, 2, ty(26))
	# temperature is intentionally not drawn on-screen per request


def draw_dancing_chinese(display, frame):
	chars = "花火節"
	base_y = 78
	base_x = 104
	spacing = 4
	wave = (-5, 0, 5, 0)
	active = frame % len(chars)
	cy = base_y

	for i, ch in enumerate(chars):
		enlarged = i == active
		shrink = 1 if enlarged else 2
		size = 32 if enlarged else 16
		x = base_x - 8 if enlarged else base_x
		y = cy + wave[(frame + i) % len(wave)]

		if enlarged:
			y -= 8

		draw_char(display, ch, x, y, shrink=shrink, wrap_y=True)
		cy += size + spacing


def blit_rotate(src, dst, angle_deg):
	# rotate src (FrameBuffer) by angle_deg degrees counter-clockwise onto dst
	w = oled_width
	h = oled_height
	angle = math.radians(angle_deg)
	cos_a = math.cos(angle)
	sin_a = math.sin(angle)
	cx = (w - 1) / 2.0
	cy = (h - 1) / 2.0
	dst.fill(0)
	for x in range(w):
		for y in range(h):
			try:
				if src.pixel(x, y):
					dx = x - cx
					dy = y - cy
					# standard CCW rotation
					xr = cx + dx * cos_a - dy * sin_a
					yr = cy + dx * sin_a + dy * cos_a
					xi = int(round(xr))
					yi = int(round(yr))
					if 0 <= xi < w and 0 <= yi < h:
						dst.pixel(xi, yi, 1)
			except Exception:
				pass


def count_bits_in_buf(buf):
	# count '1' bits in bytearray
	cnt = 0
	for b in buf:
		# builtin bit_count in Python 3.8+ not on MicroPython; use bin
		cnt += bin(b).count('1')
	return cnt


def main():
	frame = 0
	last_temp = None
	last_hum = None
	try:
		while True:
			# read DHT every 2 seconds (~8 frames at 250ms)
			if frame % 8 == 0:
				try:
					dht_sensor.measure()
					last_temp = dht_sensor.temperature()
					last_hum = dht_sensor.humidity()
					print("[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%".format(last_temp, last_hum))
				except Exception as e:
					print("[ERROR] DHT22 read failed:", e)

			temp_text = "{:.1f} C".format(last_temp) if last_temp is not None else "--.- C"
			# draw into off-screen buffer, then rotate-blit to physical oled
			try:
				src_fb.fill(0)
				draw_static_scene(src_fb, temp_text=temp_text)
				draw_dancing_chinese(src_fb, frame)
				# print debug count of src buffer bits
				try:
					bits = count_bits_in_buf(src_buf)
					print('[DEBUG] src_fb bits=', bits)
				except Exception:
					print('[DEBUG] src_fb bits count failed')
				if DEBUG_DIRECT_DRAW:
					# directly blit without rotation to test display
					try:
						oled.blit(src_fb, 0, 0)
						oled.show()
						print('[DEBUG] direct blit shown')
					except Exception as e:
						print('[ERROR] direct blit failed:', e)
				else:
					blit_rotate(src_fb, oled, 23)  # rotate left (CCW) 23 degrees
					oled.show()
			except Exception as e:
				print("[ERROR] render failed:", e)
			frame = (frame + 1) % 24
			time.sleep_ms(250)
	except KeyboardInterrupt:
		pass


if __name__ == '__main__':
	main()

