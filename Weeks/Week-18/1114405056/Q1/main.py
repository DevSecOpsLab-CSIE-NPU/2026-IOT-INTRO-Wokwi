from machine import Pin, SPI
import ili9341
import time

# 使用者學號末兩碼56 → 個位數 6
STUDENT_LAST_DIGIT = 6

# 標題顏色規則（依學號個位數）：
# 0~2 -> 黃 (255,255,0)
# 3~5 -> 青 (0,255,255)
# 6~7 -> 綠 (0,255,0)
# 8~9 -> 白 (255,255,255)


def main():
    # SPI + ILI9341 初始化（腳位固定）
    spi = SPI(2, baudrate=40_000_000, sck=Pin(18), mosi=Pin(23))
    cs = Pin(5, Pin.OUT)
    dc = Pin(17, Pin.OUT)
    display = ili9341.ILI9341(spi, cs=cs, dc=dc)

    # 從 repo 的 fonts.py 使用標題繪製函式
    from fonts import draw_title

    # 規格：每字 32px，建議每列 5 字以不超出 240px
    per_row = 5

    # 計算個位數並依規則選色
    digit = STUDENT_LAST_DIGIT % 10
    if 0 <= digit <= 2:
        color = ili9341.color565(255, 255, 0)   # 黃
    elif 3 <= digit <= 5:
        color = ili9341.color565(0, 255, 255)   # 青
    elif 6 <= digit <= 7:
        color = ili9341.color565(0, 255, 0)     # 綠
    else:
        color = ili9341.color565(255, 255, 255) # 白

    print('DEBUG: display init done, drawing title...')
    display.fill(ili9341.color565(0, 0, 0))
    try:
        # 逐列置中：計算每列實際字數，再水平置中每列；並垂直置中整個標題
        from fonts import TITLE, FONT_W, FONT_H, draw_char
        scale = 1
        ch_w = FONT_W * scale
        ch_h = FONT_H * scale
        gap_y = 6
        total = len(TITLE)
        rows = (total + per_row - 1) // per_row
        total_h = rows * ch_h + (rows - 1) * gap_y
        # 垂直置中
        y = (display.height - total_h) // 2
        for i, ch in enumerate(TITLE):
            row = i // per_row
            col = i % per_row
            chars_in_row = min(per_row, total - row * per_row)
            x_row = (display.width - chars_in_row * ch_w) // 2 - 2
            draw_char(display, ch, x_row + col * ch_w, y + row * (ch_h + gap_y), color, scale=scale)
        print('DEBUG: draw_title completed (centered per row)')
    except Exception as e:
        print('ERROR drawing title:', e)

    # 保持程式執行以便在模擬中觀察畫面
    print('DEBUG: entering idle loop')
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
