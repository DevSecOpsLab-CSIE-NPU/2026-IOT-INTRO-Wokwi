from machine import Pin
import time

led1 = Pin(5,  Pin.OUT)  # 紅
led2 = Pin(2,  Pin.OUT)  # 綠
led3 = Pin(15, Pin.OUT)  # 藍
led4 = Pin(4,  Pin.OUT)  # 黃

INTERVALS = [1000, 2000, 3000, 5000]  # ms
leds      = [led1, led2, led3, led4]
states    = [False] * 4
last      = [time.ticks_ms()] * 4

while True:
    now = time.ticks_ms()
    for i in range(4):
        if time.ticks_diff(now, last[i]) >= INTERVALS[i]:
            states[i] = not states[i]
            leds[i].value(states[i])
            last[i] = now
