from machine import Pin
import time

# 4 顆 LED 對應的 GPIO 腳位
leds = [
    Pin(5, Pin.OUT),
    Pin(2, Pin.OUT),
    Pin(4, Pin.OUT),
    Pin(16, Pin.OUT)
]

# 關閉全部 LED
def all_off():
    for led in leds:
        led.value(0)

# 目前亮的位置，從第 0 顆開始
pos = 0

# 移動方向
# 1 代表往右，-1 代表往左
direction = 1

while True:
    # 先把全部 LED 關掉，確保同一時間只有一顆亮
    all_off()

    # 讓目前位置的 LED 亮
    leds[pos].value(1)

    # 每一步間隔 0.15 秒
    time.sleep(0.15)

    # 如果到最右邊，就改成往左
    if pos == 3:
        direction = -1

    # 如果到最左邊，就改成往右
    elif pos == 0:
        direction = 1

    # 根據方向更新下一個位置
    pos = pos + direction