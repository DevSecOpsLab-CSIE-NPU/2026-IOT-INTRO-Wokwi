# Task 3: 兩顆 LED 不同間隔閃爍（使用 time.ticks_ms()）
# 說明：示範非阻塞式計時（使用 ticks_ms 與 ticks_diff）來同時控制多個輸出，避免使用多個 sleep

from machine import Pin
import time

# 設定兩顆 LED 的腳位（右側板上常見對應：可依電路圖調整）
led1 = Pin(5, Pin.OUT)  # 第一顆 LED（譬如紅燈）
led2 = Pin(2, Pin.OUT)  # 第二顆 LED（譬如綠燈）

# 間隔時間（毫秒），分別為 LED1 與 LED2 的切換週期
INTERVAL1 = 2000  # LED1 切換每 2000 ms
INTERVAL2 = 3000  # LED2 切換每 3000 ms

# 上一次切換的時間記錄（以 ticks_ms 為單位）
t1 = time.ticks_ms()
t2 = time.ticks_ms()

# 目前顯示狀態（True = ON, False = OFF）
s1 = False
s2 = False


def main():
    """主迴圈：非阻塞式地檢查是否達到各自的間隔，若達到則翻轉該 LED 的狀態。
    為什麼使用 ticks_ms/ticks_diff？
    - ticks_ms 提供上升的毫秒時脈（整數），適合用於長時間的非阻塞計時。
    - ticks_diff 用來安全地計算兩個 ticks 之差，避免整數溢位造成錯誤判斷。
    """
    global t1, t2, s1, s2

    while True:
        now = time.ticks_ms()

        # 檢查 LED1 是否已到達切換時間
        if time.ticks_diff(now, t1) >= INTERVAL1:
            s1 = not s1           # 反轉狀態
            led1.value(s1)        # 更新實際腳位輸出
            t1 = now              # 重設上一次切換時間

        # 檢查 LED2 是否已到達切換時間
        if time.ticks_diff(now, t2) >= INTERVAL2:
            s2 = not s2
            led2.value(s2)
            t2 = now


if __name__ == '__main__':
    main()
