
# 匯入所需的模組
# machine：用於硬體控制（GPIO、I2C）
# sh1107：OLED 顯示器驅動程式
# dht：DHT22 溫濕度感測器模組
# time：時間相關函式
from machine import Pin, I2C
import sh1107
import dht
import time

# ======================== 設定常數區 ========================
# 目的：定義硬體腳位、顯示器參數、動畫參數等

OLED_WIDTH = 128      # OLED 寬度（像素）
OLED_HEIGHT = 128     # OLED 高度（像素）
I2C_SCL = 21          # I2C SCL 腳位
I2C_SDA = 22          # I2C SDA 腳位
DHT_PIN = 23          # DHT22 感測器腳位
OLED_ADDR = 0x3C      # OLED I2C 位址
OLED_ROTATE = 90      # OLED 旋轉角度

CENTER_X = 64         # 畫面中心 X 座標
CENTER_Y = 64         # 畫面中心 Y 座標
DRAGON_RADIUS = 22    # 龍珠半徑
DRAGON_CX = CENTER_X - 32  # 龍珠中心 X（task4 校正）
DRAGON_CY = CENTER_Y       # 龍珠中心 Y

TEMP_INTERVAL_MS = 2000     # 溫濕度感測間隔（毫秒）
ANIM_INTERVAL_MS = 250      # 畫面動畫更新間隔（毫秒）

STUDENT_ID = "1114405020"
SHIFT_X = 0
SHIFT_Y = 0

#+ ======================== 中文點陣字型（16x16, MONO_HMSB） ========================
# 目的：定義「火」、「花」、「節」三個中文字的點陣圖，供 OLED 顯示
# 作法：每個中文字用 16x16 點陣（2 bytes * 16 rows）
# 結果：可直接繪製於 OLED 上
# 火（huǒ - fire）
FIRE = bytearray([
    0x04, 0x00,
    0x0E, 0x00,
    0x0A, 0x00,
    0x12, 0x00,
    0x22, 0x00,
    0x42, 0x10,
    0x82, 0x08,
    0x04, 0x04,
    0x08, 0x02,
    0x10, 0x01,
    0x20, 0x00,
    0x40, 0x00,
    0x80, 0x00,
    0x00, 0x00,
    0x00, 0x00,
    0x00, 0x00,
])

# 花（huā - flower）
FLOWER = bytearray([
    0x09, 0x00,
    0x09, 0x00,
    0x0F, 0x00,
    0x00, 0x00,
    0x10, 0x80,
    0x20, 0x40,
    0x40, 0x20,
    0x80, 0x10,
    0x00, 0x08,
    0x80, 0x04,
    0x40, 0x02,
    0x20, 0x01,
    0x10, 0x00,
    0x08, 0x00,
    0x04, 0x00,
    0x00, 0x00,
])

# 節（jié - festival）
FESTIVAL = bytearray([
    0x12, 0x40,
    0x12, 0x40,
    0x1E, 0x40,
    0x12, 0x40,
    0x12, 0x40,
    0x00, 0x00,
    0x1B, 0x00,
    0x12, 0x40,
    0x12, 0x40,
    0x12, 0x40,
    0x1F, 0x00,
    0x12, 0x40,
    0x12, 0x40,
    0x12, 0x40,
    0x1B, 0x00,
    0x00, 0x00,
])


# 將三個中文字型放入陣列，方便動畫輪播
CHARS = [FIRE, FLOWER, FESTIVAL]
CHAR_NAMES = ["火", "花", "節"]


# ======================== 硬體初始化 ========================
# 目的：初始化 I2C、OLED 顯示器、DHT22 感測器
i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
oled = sh1107.SH1107_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, address=OLED_ADDR, rotate=OLED_ROTATE)
dht_sensor = dht.DHT22(Pin(DHT_PIN))


# ======================== 基本繪圖函式 ========================
# 目的：提供畫圓、畫星星等基本圖形的函式
def draw_circle(display, cx, cy, r, color=1):
    x = r
    y = 0
    err = 0
    while x >= y:
        display.pixel(cx + x, cy + y, color)
        display.pixel(cx + y, cy + x, color)
        display.pixel(cx - y, cy + x, color)
        display.pixel(cx - x, cy + y, color)
        display.pixel(cx - x, cy - y, color)
        display.pixel(cx - y, cy - x, color)
        display.pixel(cx + y, cy - x, color)
        display.pixel(cx + x, cy - y, color)
        y += 1
        if err <= 0:
            err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1


# 畫五角星
def draw_star(display, cx, cy, size, color=1):
    pts = [
        (cx, cy - size),
        (cx + int(size * 0.35), cy - int(size * 0.25)),
        (cx + size, cy - int(size * 0.2)),
        (cx + int(size * 0.5), cy + int(size * 0.25)),
        (cx + int(size * 0.6), cy + size),
        (cx, cy + int(size * 0.45)),
        (cx - int(size * 0.6), cy + size),
        (cx - int(size * 0.5), cy + int(size * 0.25)),
        (cx - size, cy - int(size * 0.2)),
        (cx - int(size * 0.35), cy - int(size * 0.25)),
    ]
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        display.line(x1, y1, x2, y2, color)


# ======================== 中文字型繪製 ========================
# 目的：將 16x16 點陣中文字繪製到 OLED 上
def draw_char_bitmap(display, char_data, x, y, char_width=16, char_height=16, color=1):
    row_bytes = (char_width + 7) // 8
    for row in range(char_height):
        for col in range(char_width):
            byte_idx = row * row_bytes + col // 8
            bit_val = (char_data[byte_idx] >> (7 - (col % 8))) & 1
            if bit_val:
                display.pixel(x + col, y + row, color)


# ======================== 場景繪製函式 ========================
# 目的：繪製靜態背景、動畫中文字、溫濕度、學號等
def draw_static_scene(display, star_size=8):
    display.fill(0)

    # University info (top section)
    display.text("Penghu Univ", 4 + SHIFT_X, 0 + SHIFT_Y)
    display.text("Dept of CSIE", 4 + SHIFT_X, 10 + SHIFT_Y)
    display.text("2026", 100 + SHIFT_X, 0 + SHIFT_Y)
    draw_circle(display, DRAGON_CX + SHIFT_X, DRAGON_CY + SHIFT_Y, DRAGON_RADIUS, 1)
    draw_star(display, DRAGON_CX + SHIFT_X, DRAGON_CY + SHIFT_Y, star_size, 1)


# 動畫顯示三個中文字，輪流放大
def draw_chinese_animation(display, frame):
    base_x = 100 + SHIFT_X
    base_y = 50 + SHIFT_Y
    spacing = 4
    wave = (-5, 0, 5, 0)
    active = frame % 3
    cy = base_y

    for i in range(3):
        enlarged = (i == active)
        cell_size = 24 if enlarged else 16
        x = base_x - 4 if enlarged else base_x
        y = cy + wave[(frame + i) % 4]
        if enlarged:
            y -= 4

        draw_char_bitmap(display, CHARS[i], x, y, 16, 16)
        cy += cell_size + spacing


# 顯示溫度與濕度
def draw_temperature(display, temp_c, humidity, sensor_ok):
    x = 4 + SHIFT_X
    y = 25 + SHIFT_Y
    if sensor_ok:
        display.text("Temp:{:.1f}C".format(temp_c), x, y)
        display.text("Hum: {:.1f}%".format(humidity), x, y + 12)
    else:
        display.text("Sensor Error", x, y)
        if temp_c is not None:
            display.text("{:.1f}C".format(temp_c), x, y + 12)


def draw_student_id(display):
    display.text("ID:" + STUDENT_ID, 2 + SHIFT_X, 118 + SHIFT_Y)


# ======================== 溫濕度感測器讀取 ========================
# 目的：安全地讀取 DHT22 感測器，避免例外導致程式中斷
def read_sensor_safe(sensor):
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print("[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%".format(temp, hum))
        return temp, hum, True
    except Exception as e:
        print("[ERROR] DHT22 read failed:", e)
        return None, None, False


# ======================== 主迴圈 ========================
# 目的：定時讀取感測器、更新動畫與顯示內容
last_temp_time = 0
last_anim_time = 0
frame = 0

current_temp = 25.0    # 初始溫度
current_hum = 60.0     # 初始濕度
sensor_ok = True       # 感測器狀態

while True:
    now_ms = time.ticks_ms()  # 取得目前毫秒數

    # 每 TEMP_INTERVAL_MS 毫秒讀取一次溫濕度
    if time.ticks_diff(now_ms, last_temp_time) >= TEMP_INTERVAL_MS:
        temp, hum, ok = read_sensor_safe(dht_sensor)
        if ok:
            current_temp = temp
            current_hum = hum
        sensor_ok = ok
        last_temp_time = now_ms

    # 每 ANIM_INTERVAL_MS 毫秒更新畫面
    if time.ticks_diff(now_ms, last_anim_time) >= ANIM_INTERVAL_MS:
        # 星星大小隨溫度變化（加分功能）
        star_pulse = 6 + int((current_temp * 0.2) % 6)

        draw_static_scene(oled, star_pulse)                # 畫靜態背景與龍珠
        draw_chinese_animation(oled, frame)                # 畫動畫中文字
        draw_temperature(oled, current_temp, current_hum, sensor_ok)  # 顯示溫濕度
        draw_student_id(oled)                              # 顯示學號
        oled.show()                                       # 更新 OLED 顯示

        frame = (frame + 1) % 12
        last_anim_time = now_ms
