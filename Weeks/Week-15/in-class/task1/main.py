from machine import Pin, SPI
import ili9341
from fonts import draw_title
import time

CYAN = ili9341.color565(0, 255, 255)
BLACK = ili9341.color565(0, 0, 0)

print("[DEBUG] CYAN color565 =", hex(CYAN))

spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)
dc = Pin(17, Pin.OUT)
display = ili9341.ILI9341(spi, cs=cs, dc=dc)

display.fill(BLACK)
time.sleep_ms(100)

display.text(10, 10, "Test Cyan", CYAN)
draw_title(display, x=40, y=80, color=CYAN, scale=1, per_row=5, gap_y=16)
print("[DEBUG] Draw complete")
