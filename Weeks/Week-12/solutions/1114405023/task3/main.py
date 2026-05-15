from machine import Pin
import time

led1 = Pin(5, Pin.OUT)
led2 = Pin(2, Pin.OUT)

INTERVAL1 = 2000
INTERVAL2 = 3000

t1 = t2 = time.ticks_ms()
s1 = s2 = False

while True:
    now = time.ticks_ms()

    if time.ticks_diff(now, t1) >= INTERVAL1:
        s1 = not s1
        led1.value(s1)
        t1 = now

    if time.ticks_diff(now, t2) >= INTERVAL2:
        s2 = not s2
        led2.value(s2)
        t2 = now