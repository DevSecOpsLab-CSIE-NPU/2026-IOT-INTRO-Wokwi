from machine import Pin, SPI
from ili9341 import ILI9341, color565
from fonts import draw_title

# 固定接腳: CS=5, D/C=17, SCK=18, MOSI=23
spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))
display = ILI9341(spi, cs=Pin(5, Pin.OUT), dc=Pin(17, Pin.OUT))

BLACK = color565(0, 0, 0)
YELLOW = color565(255, 255, 0)

display.fill(BLACK)

# 5 字一列 -> 每列寬 160，使用指定置中參數
draw_title(display, x=40, y=60, color=YELLOW, scale=1, per_row=5, gap_y=8)