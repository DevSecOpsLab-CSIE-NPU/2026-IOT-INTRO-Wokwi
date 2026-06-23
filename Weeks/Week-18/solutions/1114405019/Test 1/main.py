from machine import Pin, SPI
import ili9341
from fonts import draw_title

WHITE = ili9341.color565(255, 255, 255)
BLACK = ili9341.color565(0, 0, 0)

# SPI + ILI9341 初始化
spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)
dc = Pin(17, Pin.OUT)
display = ili9341.ILI9341(spi, cs=cs, dc=dc)

# 清螢幕（黑底）
display.fill(BLACK)

# 標題「大城北游泳池空汙偵測」：每列 5 字（5*32=160px ≤ 240px）
# 水平置中 x = (240 - 5*32) / 2 = 40；兩列共高 32*2+12=76px，置中於 320px 高
draw_title(display, x=40, y=122, color=WHITE, scale=1, per_row=5, gap_y=12)
