from machine import Pin, SPI
import ili9341
from fonts import draw_title
import time

# Student/assignment info (用你的學號決定標題顏色)
STUDENT = "1114405017"

# Colors
WHITE  = ili9341.color565(255, 255, 255)
YELLOW = ili9341.color565(255, 255, 0)
CYAN   = ili9341.color565(0, 255, 255)
GREEN  = ili9341.color565(0, 255, 0)
BLACK  = ili9341.color565(0, 0, 0)

# 根據個位數決定顏色：0-2 黃, 3-5 青, 6-7 綠, 8-9 白
last = int(STUDENT[-1])
if last <= 2:
    TITLE_COLOR = YELLOW
elif 3 <= last <= 5:
    TITLE_COLOR = CYAN
elif 6 <= last <= 7:
    TITLE_COLOR = GREEN
else:
    TITLE_COLOR = WHITE

# SPI / ILI9341 pins (與 diagram.json 一致)
spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))
cs = Pin(5, Pin.OUT)
dc = Pin(17, Pin.OUT)
display = ili9341.ILI9341(spi, cs=cs, dc=dc)

# 畫面布局：置中 5 字 x 2 列（32px 字模）
display.fill(BLACK)
start_x = (240 - 5 * 32) // 2
start_y = 60
print("[INFO] starting display test")
try:
    draw_title(display, x=start_x, y=start_y, color=TITLE_COLOR, scale=1, per_row=5, gap_y=6)
    print("[INFO] draw_title ok")
except Exception as e:
    print("[ERROR] draw_title failed:", e)

# Draw a small visual test: top-left filled rect and ASCII text
display.fill_rect(0, 0, 40, 24, WHITE)
display.text(2, 2, "OK", BLACK)
print("[INFO] drawn rectangle and OK")

# 顯示靜態文字（只顯示標題與學號）
print('[INFO] drawing title and student id')
display.fill(BLACK)
draw_title(display, x=start_x, y=start_y, color=TITLE_COLOR, scale=1, per_row=5, gap_y=6)
# 在畫面下方顯示學號與提示
id_x = 10
id_y = start_y + 2 * (32 + 6) + 8
display.text(id_x, id_y, 'Student: ' + STUDENT, WHITE)
display.text(id_x, id_y + 16, 'Press Ctrl-C to stop', WHITE)
print('[INFO] done')
# 保持程式運行，不做額外更新
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print('[INFO] stopped')
        break
