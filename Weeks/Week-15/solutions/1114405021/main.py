from machine import Pin, SPI
import ili9341
from fonts import draw_title

# 學號末兩碼 21 → 個位 1 → 黃色 (255, 255, 0)
TITLE_COLOR = ili9341.color565(255, 255, 0)

spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)
dc = Pin(17, Pin.OUT)
display = ili9341.ILI9341(spi, cs=cs, dc=dc)

# Fix: MX=1 + BGR=1 (Wokwi ILI9341 needs BGR bit set for correct color)
display._write_cmd(0x36, 0x48)

display.fill(ili9341.color565(0, 0, 0))

# 10 字 × 32px = 320px > 240px，分兩列每列 5 字
# 每列寬 = 5 × 32 = 160px → 水平置中 x = (240 - 160) // 2 = 40
# 兩列高 = 32 + 6 + 32 = 70px → 垂直置中 y = (320 - 70) // 2 = 125
draw_title(display, x=40, y=125, color=TITLE_COLOR, scale=1, per_row=5, gap_y=6)
