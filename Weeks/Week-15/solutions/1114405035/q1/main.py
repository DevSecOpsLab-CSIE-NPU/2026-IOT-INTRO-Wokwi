from machine import Pin, SPI
import ili9341
from fonts import draw_title

# ===== Parameters matching Student ID: 1114405035 =====
# Title Color: Cyan (青) (Units digit = 5 -> range 3~5)
# ======================================================

# CS=GPIO5, D/C=GPIO17, MOSI=GPIO23, SCK=GPIO18
spi = SPI(2, baudrate=40000000, sck=Pin(18), mosi=Pin(23))
dc = Pin(17, Pin.OUT)
cs = Pin(5, Pin.OUT)
display = ili9341.ILI9341(spi, cs=cs, dc=dc)

# Fill screen with black
display.fill(ili9341.color565(0, 0, 0))

# Cyan color (青) is color565(0, 255, 255)
CYAN = ili9341.color565(0, 255, 255)

# Center layout for 10 characters "大城北游泳池空汙偵測":
# 5 characters per row (2 rows total). Start x = (240 - 5 * 32) / 2 = 40. Start y = 20.
# gap_y (line spacing) = 10
draw_title(display, x=40, y=20, color=CYAN, scale=1, per_row=5, gap_y=10)

print("[Q1] Title drawn successfully on ILI9341 LCD!")
