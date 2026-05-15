from machine import Pin
import time

PINS = [5, 2, 15, 4]
INTERVALS = [1000, 2000, 3000, 5000]

leds = [Pin(p, Pin.OUT) for p in PINS]
states = [False] * 4
last = [time.ticks_ms()] * 4

while True:
    now = time.ticks_ms()

    for i in range(4):
        if time.ticks_diff(now, last[i]) >= INTERVALS[i]:
            states[i] = not states[i]
            leds[i].value(states[i])
            last[i] = now