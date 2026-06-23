"""
ILI9341 TFT LCD MicroPython Driver — minimal, for Wokwi simulation.
SPI 240x320 full colour (RGB565). No RST pin needed in simulation.

Quick start:
    from machine import Pin, SPI
    from ili9341 import ILI9341, color565

    spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))
    display = ILI9341(spi, cs=Pin(5, Pin.OUT), dc=Pin(17, Pin.OUT))
    display.fill(color565(0, 0, 0))
    display.text(10, 10, "Hello!", color565(255, 255, 0))
"""

import time


def color565(r, g, b):
    return (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3


class ILI9341:

    def __init__(self, spi, cs, dc, rst=None, width=240, height=320):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.width = width
        self.height = height

        cs.init(cs.OUT, value=1)
        dc.init(dc.OUT, value=0)

        if rst is not None:
            rst.init(rst.OUT, value=1)
            rst.value(0)
            time.sleep_ms(50)
            rst.value(1)
        else:
            self._write_cmd(0x01)  # software reset
            time.sleep_ms(100)

        self._init_display()

    def _write(self, dc_val, data):
        """Write bytes to display, keeping CS low throughout."""
        self.dc.value(dc_val)
        self.cs.value(0)
        self.spi.write(data)
        self.cs.value(1)

    def _write_cmd(self, cmd, *args):
        self._write(0, bytes([cmd]))
        if args:
            self._write(1, bytes(args))

    def _write_data(self, data):
        self._write(1, data)

    def _set_window(self, x0, y0, x1, y1):
        """Set column/page window with CS low for all 3 commands."""
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(b'\x2A')
        self.dc.value(1)
        self.spi.write(bytes([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
        self.dc.value(0)
        self.spi.write(b'\x2B')
        self.dc.value(1)
        self.spi.write(bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        self.dc.value(0)
        self.spi.write(b'\x2C')
        self.cs.value(1)

    def _init_display(self):
        self._write_cmd(0xCF, 0x00, 0xC1, 0x30)
        self._write_cmd(0xED, 0x64, 0x03, 0x12, 0x81)
        self._write_cmd(0xE8, 0x85, 0x00, 0x78)
        self._write_cmd(0xCB, 0x39, 0x2C, 0x00, 0x34, 0x02)
        self._write_cmd(0xF7, 0x20)
        self._write_cmd(0xEA, 0x00, 0x00)
        self._write_cmd(0xC0, 0x23)
        self._write_cmd(0xC1, 0x10)
        self._write_cmd(0xC5, 0x3E, 0x28)
        self._write_cmd(0xC7, 0x86)
        self._write_cmd(0x36, 0x40)  # MX=1: match Wokwi ILI9341 horizontal scan direction
        self._write_cmd(0x3A, 0x55)
        self._write_cmd(0xB1, 0x00, 0x18)
        self._write_cmd(0xB6, 0x08, 0x82, 0x27)
        self._write_cmd(0xF2, 0x00)
        self._write_cmd(0x26, 0x01)
        self._write_cmd(0xE0, 0x0F, 0x31, 0x2B, 0x0C, 0x0E, 0x08, 0x4E, 0xF1,
                        0x37, 0x07, 0x10, 0x03, 0x0E, 0x09, 0x00)
        self._write_cmd(0xE1, 0x00, 0x0E, 0x14, 0x03, 0x11, 0x07, 0x31, 0xC1,
                        0x48, 0x08, 0x0F, 0x0C, 0x31, 0x36, 0x0F)
        self._write_cmd(0x11)
        time.sleep_ms(120)
        self._write_cmd(0x29)

    def _window_and_data(self, x0, y0, x1, y1, data):
        """Set column/page window then write pixel data, CS low throughout."""
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(b'\x2A')
        self.dc.value(1)
        self.spi.write(bytes([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
        self.dc.value(0)
        self.spi.write(b'\x2B')
        self.dc.value(1)
        self.spi.write(bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        self.dc.value(0)
        self.spi.write(b'\x2C')
        self.dc.value(1)
        self.spi.write(data)
        self.cs.value(1)

    def fill(self, color):
        row = color.to_bytes(2, 'big') * self.width
        x1 = self.width - 1
        y1 = self.height - 1
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(b'\x2A')
        self.dc.value(1)
        self.spi.write(bytes([0, 0, x1 >> 8, x1 & 0xFF]))
        self.dc.value(0)
        self.spi.write(b'\x2B')
        self.dc.value(1)
        self.spi.write(bytes([0, 0, y1 >> 8, y1 & 0xFF]))
        self.dc.value(0)
        self.spi.write(b'\x2C')
        self.dc.value(1)
        for _ in range(self.height):
            self.spi.write(row)
        self.cs.value(1)

    def pixel(self, x, y, color):
        self._window_and_data(x, y, x, y, color.to_bytes(2, 'big'))

    def hline(self, x, y, w, color):
        data = color.to_bytes(2, 'big') * w
        self._window_and_data(x, y, x + w - 1, y, data)

    def vline(self, x, y, h, color):
        data = color.to_bytes(2, 'big') * h
        self._window_and_data(x, y, x, y + h - 1, data)

    def fill_rect(self, x, y, w, h, color):
        data = color.to_bytes(2, 'big') * w * h
        self._window_and_data(x, y, x + w - 1, y + h - 1, data)

    def fill_circle(self, x0, y0, r, color):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self.pixel(x0 + dx, y0 + dy, color)

    def text(self, x, y, text, color, bg=None):
        from framebuf import FrameBuffer, RGB565
        n = len(text)
        w = n * 8
        h = 8
        buf = bytearray(w * h * 2)
        fbuf = FrameBuffer(buf, w, h, RGB565)
        # framebuf stores RGB565 in LE; ILI9341 expects BE — swap bytes
        c = ((color & 0xFF) << 8) | ((color & 0xFF00) >> 8)
        if bg is not None:
            b = ((bg & 0xFF) << 8) | ((bg & 0xFF00) >> 8)
            fbuf.fill(b)
        fbuf.text(text, 0, 0, c)
        self._window_and_data(x, y, x + w - 1, y + h - 1, buf)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def show(self):
        pass  # ILI9341 writes pixels immediately, no shadow framebuffer
