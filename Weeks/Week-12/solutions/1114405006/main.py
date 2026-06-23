from machine import Pin, SPI
import ili9341
import time
from fonts import draw_title

spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)
dc = Pin(17, Pin.OUT)
display = ili9341.ILI9341(spi, cs=cs, dc=dc)

BLACK = ili9341.color565(0, 0, 0)
GREEN = ili9341.color565(0, 255, 0)

display.fill(BLACK)

per_row = 5
gap_y = 6
cw = 32
ch_h = 32
total_h = ch_h * 2 + gap_y
x = (240 - per_row * cw) // 2
y = (320 - total_h) // 2

draw_title(display, x=x, y=y, color=GREEN, scale=1, per_row=per_row, gap_y=gap_y)

while True:
    time.sleep(1)
