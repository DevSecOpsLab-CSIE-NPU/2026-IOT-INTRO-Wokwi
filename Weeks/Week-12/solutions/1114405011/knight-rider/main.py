from machine import Pin
import time

# 4 顆 LED，依左到右排列（對應 diagram.json 接線）
PINS = [5, 2, 15, 4]
leds = [Pin(p, Pin.OUT) for p in PINS]

pos = 0        # 當前亮燈的位置（0 = 最左，3 = 最右）
direction = 1  # 移動方向（+1 向右，-1 向左）

def all_off():
    for led in leds:
        led.off()

while True:
    # 熄滅所有 LED
    all_off()

    # 點亮目前位置的 LED
    leds[pos].on()

    # 挑戰題：印出目前位置
    print(f"pos={pos}")

    time.sleep(0.15)

    # 移動一步
    pos += direction

    # 到達邊界時反轉方向
    if pos < 0 or pos >= len(leds):
        direction *= -1
        pos += direction * 2