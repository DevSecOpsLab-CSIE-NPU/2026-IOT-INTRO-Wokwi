from machine import Pin, I2C
import framebuf

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

    def _write_data(self):
        self.i2c.writeto(self.addr, b"\x40" + self.buf)

    def _init_display(self):
        for cmd in (
            0xAE,
            0x20,
            0x02,
            0x40,
            0xA1,
            0xC8,
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

# ESP32 I2C pin assignment for Grove SH1107 OLED (match diagram.json wiring)
i2c = I2C(0, scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 128
if sh1107 is not None:
    oled = sh1107.SH1107_I2C(oled_width, oled_height, i2c, address=0x3C, rotate=0)
    center_x = 64
    center_y = 90
else:
    oled = SH1107_I2C_FALLBACK(oled_width, oled_height, i2c, address=0x3C, rotate=0)
    # Fallback driver in this desktop flow has a different XY mapping.
    # Use empirical center so dragon ball aligns with the visible center area.
    center_x = 96
    center_y = 64


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


def draw_grid(display, cx, cy, width, height, step=16, color=1):
    for x in range(0, width, step):
        for y in range(0, height, 4):
            display.pixel(x, y, color)
    for y in range(0, height, step):
        for x in range(0, width, 4):
            display.pixel(x, y, color)
    display.hline(0, cy, width, color)
    display.vline(cx, 0, height, color)


oled.fill(0)
draw_grid(oled, center_x, center_y, oled_width, oled_height)
outer_r = min(35, center_x, oled_width - 1 - center_x, center_y, oled_height - 1 - center_y)
inner_r = max(outer_r - 3, 1)
draw_circle(oled, center_x, center_y, outer_r, 1)
draw_circle(oled, center_x, center_y, inner_r, 1)
draw_star(oled, center_x, center_y, 13, 1)
oled.show()
