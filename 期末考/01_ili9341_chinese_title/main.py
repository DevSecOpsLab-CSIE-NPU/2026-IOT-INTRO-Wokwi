from machine import Pin, SPI
import ili9341
from fonts import draw_title
import time

# 學號末兩碼：23
# 個位數 3 -> 標題顏色：青色 Cyan
TITLE_COLOR = ili9341.color565(255, 255, 0)
BLACK = ili9341.color565(0, 0, 0)

# ILI9341 SPI 固定腳位
spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))

display = ili9341.ILI9341(
    spi,
    cs=Pin(5, Pin.OUT),
    dc=Pin(17, Pin.OUT),
)

display.fill(BLACK)

# fonts.py 的 draw_title 會自動畫：
# 大城北游泳
# 池空汙偵測
draw_title(display, 40, 110, TITLE_COLOR)

print("[DEBUG] Q1 ILI9341 title displayed")

while True:
    time.sleep(1)