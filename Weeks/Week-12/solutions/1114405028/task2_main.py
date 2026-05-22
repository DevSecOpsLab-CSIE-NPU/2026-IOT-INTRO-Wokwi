# Task 2: 簡單 LED 閃爍範例（使用 Pin 5）
# 說明：連續開關 LED，並示範如何用函式封裝行為與例外處理（如中斷時將 LED 熄滅）。

from machine import Pin
import time

# 將 GPIO 5 設為輸出，用來驅動 LED
led = Pin(5, Pin.OUT)

def blink(interval=0.5):
    """
    以指定秒數為間隔持續閃爍 LED。
    - interval: 每次開或關的秒數（float）。
    使用 KeyboardInterrupt 可在開發板上中斷執行並關閉 LED。
    """
    try:
        while True:
            led.on()           # 點亮 LED
            time.sleep(interval)
            led.off()          # 熄滅 LED
            time.sleep(interval)
    except KeyboardInterrupt:
        # 若手動中斷（例如在 REPL 中按 Ctrl-C），確保 LED 被關閉
        led.off()


if __name__ == '__main__':
    blink(0.5)
