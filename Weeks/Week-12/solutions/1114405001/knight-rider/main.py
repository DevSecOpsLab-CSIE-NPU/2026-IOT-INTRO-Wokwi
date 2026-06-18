from machine import Pin
import time

# 4 LEDs from left to right
PINS = [5, 2, 15, 4]
leds = [Pin(p, Pin.OUT) for p in PINS]


def all_off():
    for led in leds:
        led.off()


pos = 0
direction = 1

while True:
    # Turn off all LEDs first
    all_off()

    # Turn on the current LED
    leds[pos].on()

    time.sleep(0.15)

    # Move one step in current direction
    pos += direction

    # Bounce at edges
    if pos < 0 or pos >= len(leds):
        direction *= -1
        pos += direction * 2
