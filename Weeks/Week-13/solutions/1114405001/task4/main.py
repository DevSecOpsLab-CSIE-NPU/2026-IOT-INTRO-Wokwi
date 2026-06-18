from machine import Pin, I2C
import sh1107
import dht
import time

# ESP32 I2C pin assignment for Grove SH1107 OLED (match diagram.json wiring)
i2c = I2C(0, scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 128
oled = sh1107.SH1107_I2C(oled_width, oled_height, i2c, address=0x3C, rotate=90)
center_x = 64
center_y = 64
# SH1107 visible center calibration (with rotate=90 on this panel)
dragon_center_x = center_x - 32
dragon_center_y = center_y

# DHT22 data pin (match diagram.json wiring)
dht_sensor = dht.DHT22(Pin(23))


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


def draw_grid(display, cx, cy, width, height, step=16, color=1):
    for x in range(0, width, step):
        for y in range(0, height, 4):
            display.pixel(x, y, color)
    for y in range(0, height, step):
        for x in range(0, width, 4):
            display.pixel(x, y, color)
    display.hline(0, cy, width, color)
    display.vline(cx, 0, height, color)


while True:
    try:
        dht_sensor.measure()
        temp_c = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        # Console debug output
        print("[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%".format(temp_c, humidity))

        # OLED display output
        oled.fill(0)
        title = "Temperature"
        temp_text = "{:.1f} C".format(temp_c)
        title_x = max(0, dragon_center_x - (len(title) * 8) // 2)
        temp_x = max(0, dragon_center_x - (len(temp_text) * 8) // 2)
        oled.text(title, title_x, 16)
        oled.text(temp_text, temp_x, 30)
        draw_circle(oled, dragon_center_x, dragon_center_y, 20, 1)
        draw_star(oled, dragon_center_x, dragon_center_y, 8, 1)
        oled.show()

    except Exception as e:
        print("[ERROR] DHT22 read failed:", e)
        oled.fill(0)
        oled.text("Sensor Error", 16, 40)
        oled.show()

    time.sleep(2)
