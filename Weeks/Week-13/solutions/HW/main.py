from machine import Pin, I2C
import time
import math
import sh1107
import dht

# =====================================
# OLED 設定
# =====================================
i2c = I2C(0, scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 128

oled = sh1107.SH1107_I2C(
    oled_width,
    oled_height,
    i2c,
    address=0x3C,
    rotate=1
)

# OLED 方向 (若需調整，可在 constructor 的 rotate 參數設定)

# =====================================
# DHT22
# =====================================
dht_sensor = dht.DHT22(Pin(23))

# =====================================
# 學號
# =====================================
STUDENT_ID = "1114405003"

# 固定顯示溫度
DISPLAY_TEMP = "24.0C"

# =====================================
# 小字型
# =====================================
FONT_3X5 = {

    "A": ("111","101","111","101","101"),
    "B": ("110","101","110","101","110"),
    "C": ("111","100","100","100","111"),
    "D": ("110","101","101","101","110"),
    "E": ("111","100","110","100","111"),
    "F": ("111","100","110","100","100"),
    "G": ("111","100","101","101","111"),
    "H": ("101","101","111","101","101"),
    "I": ("111","010","010","010","111"),
    "L": ("100","100","100","100","111"),
    "M": ("101","111","111","101","101"),
    "N": ("101","111","111","111","101"),
    "O": ("111","101","101","101","111"),
    "P": ("111","101","111","100","100"),
    "R": ("111","101","111","110","101"),
    "S": ("111","100","111","001","111"),
    "T": ("111","010","010","010","010"),
    "U": ("101","101","101","101","111"),
    "V": ("101","101","101","101","010"),
    "Y": ("101","101","010","010","010"),

    "0": ("111","101","101","101","111"),
    "1": ("010","110","010","010","111"),
    "2": ("111","001","111","100","111"),
    "3": ("111","001","111","001","111"),
    "4": ("101","101","111","001","001"),
    "5": ("111","100","111","001","111"),
    "6": ("111","100","111","101","111"),
    "7": ("111","001","001","001","001"),
    "8": ("111","101","111","101","111"),
    "9": ("111","101","111","001","111"),

    " ": ("000","000","000","000","000"),
}

# =====================================
# 畫小字
# =====================================
def draw_tiny_text(display, text, x, y):

    cursor_x = x

    for ch in text.upper():

        glyph = FONT_3X5.get(ch)

        if glyph is None:
            cursor_x += 4
            continue

        for row, bits in enumerate(glyph):

            for col, bit in enumerate(bits):

                if bit == "1":

                    display.pixel(
                        cursor_x + col,
                        y + row,
                        1
                    )

        cursor_x += 4


# =====================================
# 畫圓
# =====================================
def draw_circle(display, cx, cy, r):
    x = r
    y = 0
    err = 0

    while x >= y:
        display.pixel(cx + x, cy + y, 1)
        display.pixel(cx + y, cy + x, 1)
        display.pixel(cx - y, cy + x, 1)
        display.pixel(cx - x, cy + y, 1)
        display.pixel(cx - x, cy - y, 1)
        display.pixel(cx - y, cy - x, 1)
        display.pixel(cx + y, cy - x, 1)
        display.pixel(cx + x, cy - y, 1)

        y += 1

        if err <= 0:
            err += 2 * y + 1

        if err > 0:
            x -= 1
            err -= 2 * x + 1


# =====================================
# 畫星星
# =====================================
def draw_star(display, cx, cy, size, angle_deg=0):
    # draw a 5-point star that can be rotated by angle_deg
    angle = math.radians(angle_deg)
    cosA = math.cos(angle)
    sinA = math.sin(angle)

    base = [
        (0, -size),
        (int(size * 0.35), -int(size * 0.25)),
        (size, -int(size * 0.2)),
        (int(size * 0.5), int(size * 0.25)),
        (int(size * 0.6), size),
        (0, int(size * 0.45)),
        (-int(size * 0.6), size),
        (-int(size * 0.5), int(size * 0.25)),
        (-size, -int(size * 0.2)),
        (-int(size * 0.35), -int(size * 0.25)),
    ]

    def rot(pt):
        dx, dy = pt
        rx = dx * cosA - dy * sinA
        ry = dx * sinA + dy * cosA
        return (int(cx + rx), int(cy + ry))

    pts = [rot(p) for p in base]
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        display.line(x1, y1, x2, y2, 1)


# =====================================
# 右側直排文字 (使用位圖繪製，支援中文)
# =====================================
def glyph_pixel(data, width, x, y):
    row_bytes = (width + 7) // 8
    idx = y * row_bytes + x // 8
    if idx < 0 or idx >= len(data):
        return 0
    value = data[idx]
    return (value >> (7 - (x % 8))) & 1


# '花' 32x32
FONT_82B1 = bytearray(
    b'\x00\x00\x00\x00\x00\x7c\x1e\x00\x00\x78\x1c\x10'
    b'\x00\x78\x1c\x18\x00\x78\x1c\x3c\x7f\xff\xff\xfe'
    b'\x00\x78\x1c\x00\x00\x78\x1c\x00\x00\x78\x1c\x00'
    b'\x00\x00\x00\x00\x00\xf0\xf8\x00\x00\xf8\xf0\x00'
    b'\x01\xf0\xf0\x70\x01\xe0\xf0\xf8\x03\xc0\xf1\xf0'
    b'\x03\xc0\xf1\xe0\x07\xe0\xf3\xc0\x0f\xe0\xf7\x00'
    b'\x0d\xe0\xfc\x00\x19\xe0\xf0\x00\x31\xe0\xf0\x00'
    b'\x41\xe0\xf0\x00\x01\xe0\xf0\x04\x01\xe0\xf0\x04'
    b'\x01\xe0\xf0\x04\x01\xe0\xf0\x0c\x01\xe0\xf0\x0c'
    b'\x01\xe0\xff\xfe\x01\xe0\xff\xfe\x01\xe0\x7f\xfe'
    b'\x01\xc0\x0f\xe0\x00\x00\x00\x00'
)


# '火' 32x32
FONT_706B = bytearray(
    b'\x00\x00\x00\x00\x00\x07\x00\x00\x00\x07\x80\x00'
    b'\x00\x07\x80\x00\x00\x07\x80\x00\x00\x07\x80\x00'
    b'\x00\x07\x80\x00\x01\x07\x80\x60\x01\x07\x80\xf0'
    b'\x01\x87\xc0\xfc\x01\x87\xc1\xf0\x03\x87\xc3\xe0'
    b'\x03\x87\xc3\xc0\x07\x8f\x47\x00\x0f\x8f\x6e\x00'
    b'\x1f\x0f\x68\x00\x1f\x0f\x30\x00\x1e\x0f\x30\x00'
    b'\x00\x1e\x30\x00\x00\x1e\x38\x00\x00\x1e\x1c\x00'
    b'\x00\x3c\x1e\x00\x00\x38\x1e\x00\x00\x78\x0f\x80'
    b'\x00\xf0\x0f\xc0\x01\xe0\x07\xf0\x03\xc0\x03\xfc'
    b'\x07\x00\x01\xfe\x0e\x00\x00\xf8\x18\x00\x00\x70'
    b'\x40\x00\x00\x10\x00\x00\x00\x00'
)


# '節' 32x32
FONT_7BC0 = bytearray(
    b'\x07\x80\x38\x00\x07\x84\x7c\x18\x07\x0e\x78\x3c'
    b'\x0f\xff\x7f\xfe\x0e\xe0\xe7\x00\x1c\x70\xc3\x80'
    b'\x18\x71\x83\xc0\x30\x71\x03\xc0\x60\x74\x01\x90'
    b'\x0c\x0e\x38\x38\x0f\xff\x3f\xfc\x0e\x0f\x38\x3c'
    b'\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c\x0f\xff\x38\x3c'
    b'\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c'
    b'\x0e\x0f\x38\x3c\x0f\xff\x38\x3c\x0e\x0e\x38\x3c'
    b'\x0e\x20\x38\x3c\x0e\x38\x38\x3c\x0e\x1c\x38\xf8'
    b'\x0e\x1e\x38\x78\x1f\xff\x38\x78\x7f\xc7\x38\x60'
    b'\x7f\x07\x38\x00\x3c\x07\x38\x00\x20\x00\x38\x00'
    b'\x00\x00\x30\x00\x00\x00\x00\x00'
)

CHARS = {
    '花': (FONT_82B1, 32, 32),
    '火': (FONT_706B, 32, 32),
    '節': (FONT_7BC0, 32, 32),
}


def draw_char_pixels(display, char, x, y, shrink=1, wrap_y=False):
    if char not in CHARS:
        return
    data, w, h = CHARS[char]
    out_w = (w + shrink - 1) // shrink
    out_h = (h + shrink - 1) // shrink
    for oy in range(out_h):
        sy = oy * shrink
        for ox in range(out_w):
            sx = ox * shrink
            if sx >= w or sy >= h:
                continue
            if glyph_pixel(data, w, sx, sy):
                px = x + ox
                py = y + oy
                if wrap_y:
                    py %= oled_height
                if 0 <= px < oled_width and 0 <= py < oled_height:
                    display.pixel(px, py, 1)


def draw_text_vertical(display, text, x, y, spacing=-2, shrink=1, wrap_y=False):
    cy = y
    for ch in text:
        draw_char_pixels(display, ch, x, cy, shrink=shrink, wrap_y=wrap_y)
        _, _, h = CHARS.get(ch, (None, 0, 0))
        out_h = (h + shrink - 1) // shrink
        cy += out_h + spacing


def draw_vertical_text():
    # 將右側中文置於右上（每字有足夠間距），避免與中心圖形或學號/溫度重疊
    # 微調：左移 14 像素並稍微上移，避免字元被裁切或超出顯示區
    # 往下移 16 像素，讓三個字都能完整顯示
    draw_text_vertical(oled, '花火節', 96, 36, spacing=6, shrink=2)


def draw_firework(display, cx, cy, size=8, angle_deg=0):
    wobble_x = int(math.sin(math.radians(angle_deg)) * 2)
    wobble_y = int(math.cos(math.radians(angle_deg * 1.3)) * 2)
    cx += wobble_x
    cy += wobble_y

    angle = math.radians(angle_deg)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    spokes = [
        (0, -size),
        (int(size * 0.7), -int(size * 0.4)),
        (size, 0),
        (int(size * 0.7), int(size * 0.4)),
        (0, size),
        (-int(size * 0.7), int(size * 0.4)),
        (-size, 0),
        (-int(size * 0.7), -int(size * 0.4)),
    ]

    for dx, dy in spokes:
        rx = int(dx * cos_a - dy * sin_a)
        ry = int(dx * sin_a + dy * cos_a)
        display.line(cx, cy, cx + rx, cy + ry, 1)

    draw_circle(display, cx, cy, max(2, size // 3))
    display.pixel(cx, cy, 1)


# =====================================
# 讀取 DHT22
# =====================================
def read_temp():

    try:

        dht_sensor.measure()

        temp = dht_sensor.temperature()

        return temp

    except:

        return None


# =====================================
# 主畫面
# =====================================
def draw_screen(temp, angle_deg=0):

    oled.fill(0)

    # 左上文字
    draw_tiny_text(
        oled,
        "PENGHU UNIVERSITY",
        2,
        2
    )

    draw_tiny_text(
        oled,
        "OF SCIENCE AND TECHNOLOGY",
        2,
        10
    )

    draw_tiny_text(
        oled,
        "DEPT OF CSIE",
        2,
        18
    )

    # 年份
    oled.text("2026", 86, 2)

    # 空白背景煙花：只在邊角與上中區域輕微搖動，不碰文字與數字
    draw_firework(oled, 16, 30, 7, angle_deg)
    draw_firework(oled, 110, 30, 6, angle_deg + 45)
    draw_firework(oled, 18, 116, 6, angle_deg + 90)
    draw_firework(oled, 108, 116, 7, angle_deg + 135)


    # 中間圓圈（下移以騰出上方空間給右側中文，並讓學號/溫度顯示於圓下方）
    cx = 48
    cy = 60
    draw_circle(oled, cx, cy, 22)
    draw_circle(oled, cx, cy, 19)

    # 中間星星（跟隨圓心並可旋轉）
    draw_star(oled, cx, cy, 8, angle_deg)

    # 右邊中文字
    draw_vertical_text()

    # 在圓下方顯示學號與固定溫度（置中於圓）
    id_x = cx - (len(STUDENT_ID) * 4) // 2
    id_y = cy + 22 + 6
    temp_y = id_y + 12
    draw_tiny_text(oled, STUDENT_ID, id_x, id_y)
    oled.text(DISPLAY_TEMP, id_x, temp_y)

    oled.show()


# =====================================
# 主程式
# =====================================
angle = 0
while True:

    temp = read_temp()

    draw_screen(temp, angle)

    # 加快星星與煙花動畫速度
    angle = (angle + 25) % 360

    time.sleep(0.08)