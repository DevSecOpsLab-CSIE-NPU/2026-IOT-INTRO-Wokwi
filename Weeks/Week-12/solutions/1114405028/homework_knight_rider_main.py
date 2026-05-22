# Homework: Knight Rider 效果實作（已完成並詳註解）
# 說明：4 顆 LED 依序從左掃到右，抵達邊界後反向，持續往返，形成往返掃描燈效果。
# 程式採用簡單的索引與方向變數，不使用阻塞式多工，並處理中斷時的清理。

from machine import Pin
import time

# --- 硬體腳位設定（由左到右）
PINS = [5, 2, 15, 4]
leds = [Pin(p, Pin.OUT) for p in PINS]


def all_off():
    """將所有 LED 熄滅。呼叫此函式可確保在退出程式時板子處於安全狀態。"""
    for led in leds:
        led.off()


# 初始化參數說明：
# - pos: 目前亮的 LED 索引（0 = 最左，len(leds)-1 = 最右）
# - direction: 移動方向，+1 表示向右，-1 表示向左
pos = 0
direction = 1

# 每一步的延遲（秒）
STEP_DELAY = 0.15


def main():
    global pos, direction

    try:
        while True:
            # TODO 1（已實作）：先將所有 LED 熄滅，確保同一時間只有一顆 LED 亮
            all_off()

            # TODO 2（已實作）：點亮索引 pos 的 LED
            leds[pos].on()

            # 等待短暫時間以便視覺上看到掃描效果
            time.sleep(STEP_DELAY)

            # TODO 3（已實作）：將 pos 移動一步
            pos += direction

            # TODO 4（已實作）：若 pos 超出範圍，反轉方向並修正 pos
            if pos >= len(leds):
                # 抵達右邊界後，將位置移回到右邊界內並反向
                pos = len(leds) - 2
                direction = -1
            elif pos < 0:
                # 抵達左邊界後，將位置移回到左邊界內並反向
                pos = 1
                direction = 1

    except KeyboardInterrupt:
        # 若使用者在 REPL 中中斷（Ctrl-C），確保所有 LED 熄滅再離開
        all_off()


if __name__ == '__main__':
    main()
