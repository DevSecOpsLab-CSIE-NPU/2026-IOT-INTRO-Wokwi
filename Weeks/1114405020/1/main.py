from machine import Pin, SPI
import ili9341
from fonts import draw_title

# 學號 1114405020 個位=0 → 黃色；SPI：CS=5, D/C=17, MOSI=23, SCK=18
spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)
dc = Pin(17, Pin.OUT)
display = ili9341.ILI9341(spi, cs=cs, dc=dc)

# Wokwi ILI9341 用 BGR565（紅藍相反），故自訂 color565 交換 R↔B
def color565_bgr(r, g, b):
    return (b & 0xF8) << 8 | (g & 0xFC) << 3 | r >> 3

BLACK = 0
YELLOW = color565_bgr(255, 255, 0)
WHITE  = color565_bgr(255, 255, 255)

display.fill(BLACK)

# 10 字 × 32px = 320px > 240px → 每列 5 字 × 2 列
# 水平置中: (240 - 5×32)/2 = 40; 垂直置中: (320 - 76)/2 = 122
draw_title(display, x=40, y=122, color=YELLOW,
           scale=1, per_row=5, gap_y=6)

print("[DONE] 大城北游泳池空汙偵測（黃色）")
