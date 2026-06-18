from machine import Pin
import time

# 4 顆 LED，依左到右排列
PINS = [5, 2, 15, 4]
leds = [Pin(p, Pin.OUT) for p in PINS]

# 挑戰題：按鈕接 GPIO 18，內建 Pull-Up（按下時接 GND，讀到 0）
btn = Pin(18, Pin.IN, Pin.PULL_UP)

def all_off():
    for led in leds:
        led.off()

# -------------------------------------------------------
# Knight Rider 效果：
#   LED 從左到右掃描，到底後反向，來回不停。
#
# 變數說明：
#   pos       目前亮的 LED 索引（0 = 最左，3 = 最右）
#   direction 移動方向（+1 向右，-1 向左）
# -------------------------------------------------------

pos = 0
direction = 1

# 挑戰題：速度控制，按按鈕循環切換 慢→正常→快
SPEEDS = [0.25, 0.15, 0.08]   # 慢、正常、快
SPEED_NAMES = ["slow", "normal", "fast"]
speed_index = 1                # 預設正常速度
delay = SPEEDS[speed_index]

btn_prev = 1  # Pull-Up 閒置為高電位

while True:
    # 熄滅所有 LED
    all_off()

    # 點亮索引 pos 的 LED
    leds[pos].on()

    # 挑戰題：鏡射效果 — 同時點亮對稱位置的 LED
    mirror = len(leds) - 1 - pos
    if mirror != pos:
        leds[mirror].on()

    # 挑戰題：Serial Monitor 印出目前位置與速度
    print("pos={} speed={}".format(pos, SPEED_NAMES[speed_index]))

    time.sleep(delay)

    # 挑戰題：偵測按鈕下降緣（放開後才算一次），切換速度
    btn_now = btn.value()
    if btn_prev == 1 and btn_now == 0:   # 剛按下
        speed_index = (speed_index + 1) % len(SPEEDS)
        delay = SPEEDS[speed_index]
        print(">>> speed changed to {}".format(SPEED_NAMES[speed_index]))
    btn_prev = btn_now

    # 將 pos 移動一步（依 direction）
    pos += direction

    # 若 pos 超出範圍，反轉 direction 並修正回合法範圍
    if pos < 0 or pos >= len(leds):
        direction = -direction
        pos += 2 * direction
