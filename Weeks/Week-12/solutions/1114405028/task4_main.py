# Task 4: 四顆 LED 各自不同的週期，使用陣列簡化程式
# 說明：示範如何用列表管理多顆 LED 與對應的時間設定，程式可輕易擴充更多 LED。

from machine import Pin
import time

# LED 腳位（由左到右）。根據硬體接線調整數值
PINS = [5, 2, 15, 4]
leds = [Pin(p, Pin.OUT) for p in PINS]

# 每顆 LED 的切換週期（毫秒）
INTERVALS = [1000, 2000, 3000, 5000]

# 初始狀態（全部熄滅）
states = [False] * len(leds)

# 記錄每顆 LED 上次切換的時間（初始化為目前時間）
last = [time.ticks_ms()] * len(leds)


def main():
    """主迴圈：對每顆 LED 檢查是否到達對應的時間間隔，若是則翻轉狀態並更新輸出。"""
    while True:
        now = time.ticks_ms()
        for i in range(len(leds)):
            if time.ticks_diff(now, last[i]) >= INTERVALS[i]:
                # 翻轉狀態並設定腳位
                states[i] = not states[i]
                leds[i].value(states[i])
                last[i] = now


if __name__ == '__main__':
    main()
