from machine import Pin, I2C
import sh1107
import dht
import time
import framebuf

# ---------------------
# Configurable constants
# ---------------------
I2C_SCL = 21
I2C_SDA = 22
DHT_PIN = 23
OLED_ADDR = 0x3C
OLED_WIDTH = 128
OLED_HEIGHT = 128
ROTATE = 90
STUDENT_ID = "1114405028"
FRAME_DELAY_MS = 200        # 動畫每幀更新間隔（ms）
SENSOR_INTERVAL_MS = 2000  # DHT22 讀值間隔（ms）

# initialize hardware
i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
oled = sh1107.SH1107_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, address=OLED_ADDR, rotate=ROTATE)
center_x = OLED_WIDTH // 2
center_y = OLED_HEIGHT // 2
# 調整主視覺中心（依 rotate 可能需要微調）
dragon_center_x = center_x - 32
dragon_center_y = center_y

# DHT sensor
dht_sensor = dht.DHT22(Pin(DHT_PIN))

# === 中文字型（取自 in-class/task2, 32x32） ===
# '花'  32x32
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
# '火'  32x32
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
# '節'  32x32
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

# === 基本繪製工具（來自 in-class/task2） ===

def draw_char(oled, char, x, y, shrink=1):
    if char not in CHARS:
        return
    data, w, h = CHARS[char]
    fb = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
    if shrink <= 1:
        oled.blit(fb, x, y)
        return
    out_w = (w + shrink - 1) // shrink
    out_h = (h + shrink - 1) // shrink
    for oy in range(out_h):
        sy = oy * shrink
        for ox in range(out_w):
            sx = ox * shrink
            if fb.pixel(sx, sy):
                oled.pixel(x + ox, y + oy, 1)


def draw_text_vertical(oled, text, x, y, spacing=0, shrink=1, wrap_y=False):
    cy = y
    for ch in text:
        if ch in CHARS:
            _, _, h = CHARS[ch]
            draw_char(oled, ch, x, cy, shrink=shrink)
            draw_h = (h + shrink - 1) // shrink
            cy += draw_h + spacing
            if wrap_y and cy > OLED_HEIGHT:
                cy = 0


# simple decorative shapes

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


# ---------------------
# Screen drawing helpers
# ---------------------

def draw_static_scene(oled):
    oled.fill(0)
    # decorative center (dragon / circle + star)
    draw_circle(oled, dragon_center_x, dragon_center_y, 28, 1)
    draw_star(oled, dragon_center_x, dragon_center_y, 9, 1)
    # English title area
    oled.text("SH1107 Temp", 4, 4)
    # student id visible on screen as required
    oled.text(STUDENT_ID, 4, 18)


def draw_temperature(oled, temp_c):
    temp_text = "{:.1f} C".format(temp_c)
    # place temperature left of center
    tx = max(0, dragon_center_x - (len(temp_text) * 8) // 2)
    oled.text("Temp:", tx, 36)
    oled.text(temp_text, tx, 48)


def draw_chinese_animation(oled, frame):
    # 花火節 直排在右側，採用縮放與上下波動效果
    chars = "花火節"
    x = 100
    base_y = 12
    spacing = 2
    # 週期化的縮放效果：在 frame 範圍內切換 shrink
    # shrink=2 -> 字體 32x32 -> 顯示 16x16
    shrink_list = [2, 1, 2, 1]
    shrink = shrink_list[frame % len(shrink_list)]
    # wave offset
    offset = int(3 * (1 if ((frame // 2) % 2) == 0 else -1))
    draw_text_vertical(oled, chars, x, base_y + offset, spacing=spacing, shrink=shrink, wrap_y=True)


# safe read sensor
def read_sensor_safe():
    try:
        dht_sensor.measure()
        t = dht_sensor.temperature()
        h = dht_sensor.humidity()
        print("[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%".format(t, h))
        return t, h, None
    except Exception as e:
        print("[ERROR] DHT22 read failed:", e)
        return None, None, e


def main():
    last_frame_time = time.ticks_ms()
    last_sensor_time = time.ticks_ms() - SENSOR_INTERVAL_MS
    frame = 0
    last_valid_temp = None

    while True:
        now = time.ticks_ms()
        # A: update animation frame
        if time.ticks_diff(now, last_frame_time) >= FRAME_DELAY_MS:
            # draw whole scene each frame
            draw_static_scene(oled)
            draw_chinese_animation(oled, frame)
            # draw last known temp if available
            if last_valid_temp is not None:
                draw_temperature(oled, last_valid_temp)
            oled.show()
            frame += 1
            last_frame_time = now

        # B: read sensor every SENSOR_INTERVAL_MS
        if time.ticks_diff(now, last_sensor_time) >= SENSOR_INTERVAL_MS:
            t, h, err = read_sensor_safe()
            if err is None and t is not None:
                last_valid_temp = t
            else:
                # show error on screen (non-blocking)
                oled.fill(0)
                oled.text("Sensor Error", 16, 40)
                oled.show()
            last_sensor_time = now

        # small sleep to yield
        time.sleep_ms(10)


if __name__ == '__main__':
    main()
