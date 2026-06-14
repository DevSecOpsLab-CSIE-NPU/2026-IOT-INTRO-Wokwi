from machine import Pin
import time

# 假設助教電路接在 GPIO 4, 16, 17, 5 (這部分依你們課堂電路為準，可自行修改腳位)
leds = [Pin(4, Pin.OUT), Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(5, Pin.OUT)]

def all_off():
    for led in leds:
        led.off()

pos = 0          # 一開始在最左邊 (第 0 顆)
direction = 1    # 1 代表向右，-1 代表向左

while True:
    all_off()           # 1. 先把所有的燈熄滅
    leds[pos].on()      # 2. 只點亮目前位置的燈
    
    time.sleep(0.15)    # 3. 每步間隔 0.15 秒
    
    # 4. 移動到下一步
    pos += direction
    
    # 5. 判斷是否撞牆，撞牆就反轉方向
    if pos == 3:
        direction = -1   # 走到最右邊，改向左
    elif pos == 0:
        direction = 1    # 走到最左邊，改向右
