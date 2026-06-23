import time
from machine import Pin, SPI
# 1. 導入顯示器驅動與專用字型函式
from ili9341 import ILI9341, color565
from fonts import draw_title

# --- [2. 硬體初始化] ---
# 降低波特率至 20MHz，確保 SPI 順利驅動不報錯
spi = SPI(1, baudrate=20_000_000, sck=Pin(18), mosi=Pin(23))
display = ILI9341(spi, cs=Pin(5, Pin.OUT), dc=Pin(17, Pin.OUT))

# --- [3. 定義顏色] ---
# 針對模擬器紅藍反轉修正：(0, 255, 255) 傳入反轉後，會在畫面上呈現完美的黃色
YELLOW = color565(0, 255, 255)  
BLACK = color565(0, 0, 0)

# 清除螢幕背景為黑色
display.fill(BLACK)

# --- [4. 自動置中排版計算] ---
start_x = 40  
start_y = 120  

# --- [5. 呼叫函式一行流繪製（主循環外，只畫一次不閃爍）] ---
draw_title(display, x=start_x, y=start_y, color=YELLOW, scale=1)

print("第一題：使用自動排版函式繪製黃色中文招牌成功！")

# --- [6. 後續題目主循環預留] ---
while True:
    time.sleep(1)