from machine import Pin, SPI
import time
from fonts import draw_title


# 第一題：ESP32 + ILI9341 中文標題顯示
# 學號：1114405014，個位數 4 => CYAN

SCREEN_W = 240
SCREEN_H = 320

# 對齊目前 diagram.json
PIN_CS = 5
PIN_DC = 17
PIN_SCK = 18
PIN_MOSI = 23

TITLE_X = 40
TITLE_Y = 120
PER_ROW = 5
GAP_Y = 8


def color565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


BLACK = color565(0, 0, 0)
CYAN = color565(0, 255, 255)


class ILI9341:
    def __init__(self, spi, cs, dc, width=240, height=320):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.width = width
        self.height = height

        self.cs.init(Pin.OUT, value=1)
        self.dc.init(Pin.OUT, value=0)

        self.init_display()

    def _write_cmd(self, cmd):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)

    def _write_data(self, data):
        self.cs.value(0)
        self.dc.value(1)
        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        self.cs.value(1)

    def _set_window(self, x0, y0, x1, y1):
        self._write_cmd(0x2A)
        self._write_data(bytearray([
            x0 >> 8, x0 & 0xFF,
            x1 >> 8, x1 & 0xFF
        ]))

        self._write_cmd(0x2B)
        self._write_data(bytearray([
            y0 >> 8, y0 & 0xFF,
            y1 >> 8, y1 & 0xFF
        ]))

        self._write_cmd(0x2C)

    def _window_and_data(self, x0, y0, x1, y1, data):
        self._set_window(x0, y0, x1, y1)
        self._write_data(data)

    def fill(self, color):
        hi = color >> 8
        lo = color & 0xFF

        block_pixels = 240
        block = bytearray()
        for _ in range(block_pixels):
            block.append(hi)
            block.append(lo)

        self._set_window(0, 0, self.width - 1, self.height - 1)

        total_pixels = self.width * self.height
        sent = 0

        self.cs.value(0)
        self.dc.value(1)

        while sent < total_pixels:
            n = min(block_pixels, total_pixels - sent)
            self.spi.write(block[:n * 2])
            sent += n

        self.cs.value(1)

    def init_display(self):
        time.sleep_ms(100)

        self._write_cmd(0x01)
        time.sleep_ms(150)

        self._write_cmd(0x11)
        time.sleep_ms(150)

        self._write_cmd(0x3A)
        self._write_data(0x55)

        # 直向顯示：240 x 320
        self._write_cmd(0x36)
        self._write_data(0x48)

        self._write_cmd(0x29)
        time.sleep_ms(100)


def main():
    spi = SPI(
        2,
        baudrate=20000000,
        polarity=0,
        phase=0,
        sck=Pin(PIN_SCK),
        mosi=Pin(PIN_MOSI)
    )

    display = ILI9341(
        spi=spi,
        cs=Pin(PIN_CS),
        dc=Pin(PIN_DC),
        width=SCREEN_W,
        height=SCREEN_H
    )

    display.fill(BLACK)

    draw_title(
        display,
        x=TITLE_X,
        y=TITLE_Y,
        color=CYAN,
        scale=1,
        per_row=PER_ROW,
        gap_y=GAP_Y
    )

    print("[TASK1] Display ready")
    print("[TASK1] Title: 大城北游泳池空汙偵測")
    print("[TASK1] Color: CYAN")
    print("[TASK1] Pins: CS=5, DC=17, SCK=18, MOSI=23")


main()