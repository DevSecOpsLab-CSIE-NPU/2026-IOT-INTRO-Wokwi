INTERVAL1 = 2000  # 紅 LED 2 秒
INTERVAL2 = 3000  # 綠 LED 3 秒

t1 = t2 = time.ticks_ms()
s1 = s2 = False

while True:
    now = time.ticks_ms()

    # 紅 LED
    if time.ticks_diff(now, t1) >= INTERVAL1:
        s1 = not s1
        led1.value(s1)
        t1 = now

    # 綠 LED
    if time.ticks_diff(now, t2) >= INTERVAL2:
        s2 = not s2
        led2.value(s2)
        t2 = now

    time.sleep_ms(1)
