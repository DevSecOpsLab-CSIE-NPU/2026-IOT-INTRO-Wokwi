# Week 13 Homework
# SH1107 + DHT22 中文動畫溫度看板
# Student ID: 1114405023
#
# This version follows the in-class task4 SH1107 wiring:
# - OLED SCL -> GPIO21
# - OLED SDA -> GPIO22
# - DHT22 DATA/SDA -> GPIO23
# - SH1107 init uses address=0x3C and rotate=90

from machine import Pin, I2C
import time
import math
import dht
import sh1107

# =========================
# Tunable constants
# =========================
OLED_WIDTH = 128
OLED_HEIGHT = 128
OLED_ADDR = 0x3C

# Match in-class task4 wiring
I2C_SCL_PIN = 21
I2C_SDA_PIN = 22
DHT_PIN = 23

# Required by homework: keep adjustable constants.
center_x = 64
center_y = 64
# In-class task4 used this calibration because Wokwi SH1107 visible center is shifted.
offset = -32
dragon_center_x = center_x + offset
dragon_center_y = center_y

FRAME_DELAY_MS = 250       # animation frame update: 200~300 ms
SENSOR_INTERVAL_MS = 2000  # DHT22 update interval: 2 seconds
STUDENT_ID = "1114405023"

# Last valid sensor values. If DHT22 fails temporarily, keep them.
last_temp_c = 24.0
last_humidity = 50.0
sensor_ok = False

# =========================
# Hardware init
# =========================
print("MAIN START: Week13 SH1107 DHT22 homework")
i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=400000)
print("I2C scan:", i2c.scan())
oled = sh1107.SH1107_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, address=OLED_ADDR, rotate=90)
sensor = dht.DHT22(Pin(DHT_PIN))

# =========================
# Chinese 16x16 bitmap font: 花火節
# =========================
FONT_16 = {
    "花": [
        "0001100000011000",
        "0111111001111110",
        "0001100000011000",
        "0000000000000000",
        "1111111111111111",
        "0001100000110000",
        "0001100001100000",
        "0001100011000000",
        "0011111111111000",
        "0110110000011000",
        "1100110000011000",
        "0000110000011000",
        "0000110000011000",
        "0000110000110000",
        "0000110011100000",
        "0000000000000000",
    ],
    "火": [
        "0000000110000000",
        "0000000110000000",
        "0000000110000000",
        "0000000110000000",
        "0000100110010000",
        "0001100110011000",
        "0001100110011000",
        "0011000110001100",
        "0011000110001100",
        "0110000110000110",
        "1100000110000011",
        "0000001111000000",
        "0000011001100000",
        "0000110000110000",
        "0011000000001100",
        "1100000000000011",
    ],
    "節": [
        "0010010000100100",
        "0111111001111110",
        "0100100001001000",
        "0000000000000000",
        "0111111111111000",
        "0100000000001000",
        "0111111111111000",
        "0100000000001000",
        "0111111111111000",
        "0000001100000000",
        "0011111111110000",
        "0010001100010000",
        "0011111111110000",
        "0000001100000000",
        "0000001100000000",
        "0000011000000000",
    ],
}

# =========================
# Drawing helpers
# =========================
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


def fill_rect(display, x, y, w, h, color=1):
    # Some MicroPython framebuf builds have fill_rect; this wrapper keeps it safe.
    try:
        display.fill_rect(x, y, w, h, color)
    except AttributeError:
        for yy in range(y, y + h):
            display.hline(x, yy, w, color)


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


def draw_chinese_char(display, ch, x, y, color=1, scale=1):
    rows = FONT_16.get(ch)
    if not rows:
        return
    for row_idx, row in enumerate(rows):
        for col_idx, bit in enumerate(row):
            if bit == "1":
                if scale == 1:
                    display.pixel(x + col_idx, y + row_idx, color)
                else:
                    fill_rect(display, x + col_idx * scale, y + row_idx * scale, scale, scale, color)


def draw_chinese_animation(display, frame):
    # Layout order requested:
    # temperature / humidity -> dragon ball -> 花火節 -> student ID
    text = "花火節"
    base_x = 36
    base_y = 84

    offsets = [0, -1, 0, 1]
    for i, ch in enumerate(text):
        y = base_y + offsets[(frame + i) % len(offsets)]
        draw_chinese_char(display, ch, base_x + i * 17, y, 1)

    # Small sparkle animation near the Chinese text.
    if frame % 4 < 2:
        sx, sy = 26, 92
    else:
        sx, sy = 94, 92

    display.pixel(sx, sy, 1)
    display.pixel(sx - 1, sy, 1)
    display.pixel(sx + 1, sy, 1)
    display.pixel(sx, sy - 1, 1)
    display.pixel(sx, sy + 1, 1)


def draw_static_scene(display, frame):
    # Requested vertical layout:
    # 溫度 / 濕度
    # 龍珠
    # 花火節
    # 學號
    #
    # Short labels avoid SH1107 rotate=90 wrap/clipping.

    # 1. Temperature and humidity block
    display.hline(0, 37, 128, 1)

    # 2. Dragon Ball visual
    pulse = 1 if frame % 8 < 4 else 0
    r = 17 + pulse
    cx = dragon_center_x
    cy = 61

    draw_circle(display, cx, cy, r, 1)
    draw_circle(display, cx, cy, r - 2, 1)
    draw_star(display, cx, cy - 2 + (frame % 3) - 1, 6, 1)
    draw_star(display, cx - 8, cy + 6, 3, 1)
    draw_star(display, cx + 8, cy + 6, 3, 1)

    # 3. Bottom student ID area
    display.hline(0, 107, 128, 1)
    display.text("ID:" + STUDENT_ID[-5:], 29, 116)


def draw_temperature(display, temp_c, humidity, ok):
    # 1st row: temperature. 2nd row: humidity.
    # Use compact English labels because MicroPython text() cannot render Chinese.
    if ok:
        display.text("TEMP:{:.1f}C".format(temp_c), 18, 5)
        display.text("HUMI:{:.0f}%".format(humidity), 18, 22)
    else:
        display.text("TEMP:--.-C", 18, 5)
        display.text("HUMI:--%", 18, 22)


def read_sensor_safe(prev_temp, prev_humidity):
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print("[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%".format(temp, hum))
        return temp, hum, True
    except Exception as e:
        print("[ERROR] DHT22 read failed:", e)
        return prev_temp, prev_humidity, False

# =========================
# Main loop
# =========================
frame = 0
last_sensor_ms = time.ticks_ms() - SENSOR_INTERVAL_MS

while True:
    now = time.ticks_ms()

    if time.ticks_diff(now, last_sensor_ms) >= SENSOR_INTERVAL_MS:
        last_temp_c, last_humidity, sensor_ok = read_sensor_safe(last_temp_c, last_humidity)
        last_sensor_ms = now

    oled.fill(0)
    draw_static_scene(oled, frame)
    draw_chinese_animation(oled, frame)
    draw_temperature(oled, last_temp_c, last_humidity, sensor_ok)
    oled.show()

    frame += 1
    time.sleep_ms(FRAME_DELAY_MS)
