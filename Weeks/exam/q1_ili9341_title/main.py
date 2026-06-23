from machine import Pin, SPI
from framebuf import FrameBuffer, MONO_HLSB
import ili9341
import fonts


TFT_CS = 5
TFT_DC = 17
TFT_MOSI = 23
TFT_SCK = 18

TITLE_COLOR = ili9341.color565(255, 255, 255)
BLACK = ili9341.color565(0, 0, 0)

TITLE_LINE_1 = "大城北游泳"
TITLE_LINE_2 = "池空汙偵測"


def draw_chinese_char(display, ch, x, y, color):
    data, width, height = fonts.CHARS[ch]
    fb = FrameBuffer(bytearray(data), width, height, MONO_HLSB)
    for row in range(height):
        for col in range(width):
            if fb.pixel(col, row):
                display.pixel(x + col, y + row, color)


def draw_chinese_text(display, text, x, y, color):
    cursor_x = x
    for ch in text:
        draw_chinese_char(display, ch, cursor_x, y, color)
        cursor_x += 32


spi = SPI(2, baudrate=40_000_000, sck=Pin(TFT_SCK), mosi=Pin(TFT_MOSI))
display = ili9341.ILI9341(spi, cs=Pin(TFT_CS, Pin.OUT), dc=Pin(TFT_DC, Pin.OUT))

display.fill(BLACK)
x = (240 - 160) // 2
draw_chinese_text(display, TITLE_LINE_1, x, 88, TITLE_COLOR)
draw_chinese_text(display, TITLE_LINE_2, x, 128, TITLE_COLOR)
