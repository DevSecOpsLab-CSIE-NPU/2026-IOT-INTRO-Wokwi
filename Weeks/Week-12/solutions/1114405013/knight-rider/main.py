from machine import Pin
import time

# 4 顆 LED，依照題目指定的 GPIO 腳位
leds = [
    Pin(5, Pin.OUT),
    Pin(2, Pin.OUT),
    Pin(15, Pin.OUT),
    Pin(4, Pin.OUT),
]

def all_off():
    # 關掉所有 LED
    for led in leds:
        led.off()

# pos 代表目前亮哪一顆 LED
pos = 0

# direction 代表移動方向
# 1 表示往右，-1 表示往左
direction = 1

while True:
    # 1. 先熄滅所有 LED
    all_off()

    # 2. 點亮目前位置的 LED
    leds[pos].on()

    # 3. 停留一小段時間
    time.sleep(0.15)

    # 4. 移動到下一個位置
    pos = pos + direction

    # 5. 如果走到最右邊之後超出範圍，就反轉方向
    if pos >= len(leds):
        direction = -1
        pos = len(leds) - 2

    # 6. 如果走到最左邊之後超出範圍，也反轉方向
    elif pos < 0:
        direction = 1
        pos = 1