from machine import Pin, SPI

import ili9341
from fonts import draw_title, draw_char


print("Task1 main.py started")

SCREEN_WIDTH = 240
CHAR_SIZE = 32
CHARS_PER_ROW = 5
TITLE_WIDTH = CHARS_PER_ROW * CHAR_SIZE
TITLE_X = (SCREEN_WIDTH - TITLE_WIDTH) // 2
TITLE_Y = 96
LINE_GAP = 8

BLACK = ili9341.color565(0, 0, 0)
CYAN = 0xFF07

spi = SPI(
    2,
    baudrate=40_000_000,
    sck=Pin(18),
    mosi=Pin(23)
)

display = ili9341.ILI9341(
    spi,
    cs=Pin(5, Pin.OUT),
    dc=Pin(17, Pin.OUT)
)

display.fill(BLACK)

draw_title(
    display,
    x=TITLE_X,
    y=TITLE_Y,
    color=CYAN,
    scale=1,
    per_row=CHARS_PER_ROW,
    gap_y=LINE_GAP
)

print("Task1 display done")
