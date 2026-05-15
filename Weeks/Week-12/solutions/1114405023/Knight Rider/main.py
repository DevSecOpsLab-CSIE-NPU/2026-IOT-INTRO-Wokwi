from machine import Pin
import time

PINS = [5, 2, 15, 4]
leds = [Pin(p, Pin.OUT) for p in PINS]

pos = 0
direction = 1
DELAY = 0.15

def all_off():
    for led in leds:
        led.off()

while True:
    all_off()
    leds[pos].on()
    print("pos=", pos)

    time.sleep(DELAY)

    pos += direction

    if pos == 3:
        direction = -1
    elif pos == 0:
        direction = 1