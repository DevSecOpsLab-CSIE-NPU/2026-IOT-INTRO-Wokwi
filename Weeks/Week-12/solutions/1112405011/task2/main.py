from machine import Pin
import time

led = Pin(5, Pin.OUT)   # GPIO5 設為輸出

while True:
    led.on()            # 點亮
    time.sleep(0.5)     # 等 0.5 秒
    led.off()           # 熄滅
    time.sleep(0.5)     # 等 0.5 秒
