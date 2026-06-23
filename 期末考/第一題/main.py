from machine import Pin, SPI
import time
import ili9341
import fonts

# 題目指定標題顏色：RGB(225, 225, 0)。
# Wokwi ILI9341 目前會紅藍通道對調，因此送入硬體前先做補償，畫面才會是黃色。
TITLE_RGB = (225, 225, 0)
YELLOW = ili9341.color565(TITLE_RGB[2], TITLE_RGB[1], TITLE_RGB[0])
BLACK = ili9341.color565(0, 0, 0)

# diagram.json 接線：CS=GPIO5, DC=GPIO17, MOSI=GPIO23, SCK=GPIO18。
spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)
dc = Pin(17, Pin.OUT)
display = ili9341.ILI9341(spi, cs=cs, dc=dc)

# 只顯示 32px 黃色標題，並放在 240x320 版面的正中央。
display.fill(BLACK)
fonts.draw_title(display, fonts.TITLE_X, fonts.TITLE_Y, YELLOW)

while True:
    time.sleep(1)
