from machine import Pin, I2C
import framebuf


class SSD1306_I2C(framebuf.FrameBuffer):
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
			0xAE,  # display off
			0x20,
			0x00,  # horizontal addressing mode
			0x40,  # start line
			0xA1,  # seg remap
			0xC8,  # com scan dec
			0x81,
			0x7F,  # contrast
			0xA6,  # normal display
			0xA8,
			0x3F,  # multiplex ratio for 64px
			0xD3,
			0x00,  # display offset
			0xD5,
			0x80,  # display clock
			0xD9,
			0xF1,  # pre-charge
			0xDA,
			0x12,  # com pins
			0xDB,
			0x30,  # vcom detect
			0x8D,
			0x14,  # charge pump
			0xAF,  # display on
		):
			self._write_cmd(cmd)
		self.fill(0)
		self.show()

	def show(self):
		self._write_cmd(0x21)  # column addr
		self._write_cmd(0)
		self._write_cmd(self.width - 1)
		self._write_cmd(0x22)  # page addr
		self._write_cmd(0)
		self._write_cmd(self.pages - 1)
		self._write_data()

# ESP32 I2C pin assignment for SSD1306
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Dragon Ball inspired style tags shown on OLED
oled.fill(0)
oled.text("DRAGON BALL", 8, 8)
oled.text("spiky hair", 16, 24)
oled.text("speed lines", 12, 36)
oled.text("energy aura", 10, 48)
oled.show()
