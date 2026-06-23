# main.py - Step 1: TFT 中文標題
from machine import Pin, SPI
import ili9341
from fonts import draw_title
import time

# 顏色
BLACK = ili9341.color565(0, 0, 0)
# 針對此 ILI9341 驅動 + Wokwi 做位元組交換，才能得到正確顯示顏色
def rgb565_swap(c):
    return ((c & 0xFF) << 8) | ((c & 0xFF00) >> 8)
CYAN = rgb565_swap(ili9341.color565(0, 255, 255))   # 學號對應標題顏色

# TFT 初始化
spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)
dc = Pin(17, Pin.OUT)
tft = ili9341.ILI9341(spi, cs=cs, dc=dc)

# 清除背景
tft.fill(BLACK)

# 繪製「大城北游泳池空汙偵測」
# 10 個字，每列 5 字；x = (240 - 5 * 32) // 2 = 40
draw_title(tft, 40, 40, CYAN, scale=1, per_row=5, gap_y=8)
print("[DEBUG] TFT title drawn")

# 保持程式運行
while True:
    time.sleep(1)
