# pyright: reportMissingImports=false
from machine import Pin, SPI
import time
import ili9341
from fonts import draw_title

WHITE = ili9341.color565(255, 255, 255)
PINK = ili9341.color565(255, 0, 255)

spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)
dc = Pin(17, Pin.OUT)
display = ili9341.ILI9341(spi, cs=cs, dc=dc)

display.fill(0)
draw_title(display, x=40, y=120, color=PINK, scale=1, per_row=5, gap_y=6)

while True:
    time.sleep(1)
