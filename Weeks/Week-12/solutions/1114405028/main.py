from machine import Pin
import time

# --- 硬體腳位設定（由左到右）
PINS = [5, 2, 15, 4]
leds = [Pin(p, Pin.OUT) for p in PINS]


def all_off():
    """將所有 LED 熄滅，確保同一時間只有一顆 LED 亮。"""
    for led in leds:
        led.off()


# 初始化參數
pos = 0
direction = 1
STEP_DELAY = 0.15


def main():
    global pos, direction

    try:
        while True:
            all_off()
            leds[pos].on()
            time.sleep(STEP_DELAY)

            pos += direction

            if pos >= len(leds):
                pos = len(leds) - 2
                direction = -1
            elif pos < 0:
                pos = 1
                direction = 1

    except KeyboardInterrupt:
        all_off()


if __name__ == '__main__':
    main()
