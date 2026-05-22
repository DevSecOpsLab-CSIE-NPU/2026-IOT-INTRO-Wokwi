from machine import Pin, I2C
import framebuf
import dht
import time

try:
    import sh1107  # type: ignore
except ImportError:
    sh1107 = None


class SH1107_I2C_FALLBACK(framebuf.FrameBuffer):
    def __init__(self, width, height, i2c, address=0x3C, rotate=0):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = address
        self.rotate = rotate
        self.pages = self.height // 8
        self.buf = bytearray(self.pages * self.width)
        super().__init__(self.buf, self.width, self.height, framebuf.MONO_VLSB)
        self._init_display()

    def _write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytearray((0x80, cmd)))

    def _init_display(self):
        for cmd in (
            0xAE,
            0x20,
            0x02,
            0x40,
            0xA0,
            0xC0,
            0x81,
            0x7F,
            0xA6,
            0xA8,
            0x7F,
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
        for page in range(self.pages):
            self._write_cmd(0xB0 | page)
            self._write_cmd(0x00)
            self._write_cmd(0x10)
            start = page * self.width
            end = start + self.width
            self.i2c.writeto(self.addr, b"\x40" + self.buf[start:end])


OLED_WIDTH = 128
OLED_HEIGHT = 128

# Wiring from diagram.json
i2c = I2C(0, scl=Pin(21), sda=Pin(22))
dht_sensor = dht.DHT22(Pin(23))

if sh1107 is not None:
    oled = sh1107.SH1107_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, address=0x3C, rotate=90)
else:
    oled = SH1107_I2C_FALLBACK(OLED_WIDTH, OLED_HEIGHT, i2c, address=0x3C, rotate=90)

# Calibrated visual center for Wokwi SH1107
dragon_center_x = 32
dragon_center_y = 64


def put_pixel(display, x, y, color=1):
    if 0 <= x < OLED_WIDTH and 0 <= y < OLED_HEIGHT:
        display.pixel(x, y, color)


def draw_circle(display, cx, cy, r, color=1):
    x = r
    y = 0
    err = 0
    while x >= y:
        put_pixel(display, cx + x, cy + y, color)
        put_pixel(display, cx + y, cy + x, color)
        put_pixel(display, cx - y, cy + x, color)
        put_pixel(display, cx - x, cy + y, color)
        put_pixel(display, cx - x, cy - y, color)
        put_pixel(display, cx - y, cy - x, color)
        put_pixel(display, cx + y, cy - x, color)
        put_pixel(display, cx + x, cy - y, color)
        y += 1
        if err <= 0:
            err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1


def draw_star(display, cx, cy, size, color=1):
    pts = (
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
    )
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        display.line(x1, y1, x2, y2, color)


def draw_screen(temp_c):
    oled.fill(0)

    title = "Temperature"
    temp_text = "{:.1f} C".format(temp_c)
    title_x = max(0, dragon_center_x - (len(title) * 8) // 2)
    temp_x = max(0, dragon_center_x - (len(temp_text) * 8) // 2)

    oled.text(title, title_x, 16)
    oled.text(temp_text, temp_x, 30)

    draw_circle(oled, dragon_center_x, dragon_center_y, 20, 1)
    draw_star(oled, dragon_center_x, dragon_center_y, 8, 1)
    oled.show()


def draw_error_screen():
    oled.fill(0)
    oled.text("Sensor Error", 16, 40)
    oled.show()


while True:
    try:
        dht_sensor.measure()
        temp_c = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        print("[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%".format(temp_c, humidity))
        draw_screen(temp_c)
    except Exception as e:
        print("[ERROR] DHT22 read failed:", e)
        draw_error_screen()

    time.sleep(2)
