from machine import Pin, I2C
import sh1107

# ESP32 I2C pin assignment for Grove SH1107 OLED (match diagram.json wiring)
i2c = I2C(0, scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 128
oled = sh1107.SH1107_I2C(oled_width, oled_height, i2c, address=0x3C, rotate=0)

center_x = 64
center_y = 90


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

from machine import Pin, I2C
import sh1107
import time
import math

# ESP32 I2C pin assignment for Grove SH1107 OLED (match diagram.json wiring)
i2c = I2C(0, scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 128
oled = sh1107.SH1107_I2C(oled_width, oled_height, i2c, address=0x3C, rotate=0)

center_x = oled_width // 2
center_y = 90


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


def rotated_point(px, py, cx, cy, angle):
    s = math.sin(angle)
    c = math.cos(angle)
    x = px - cx
    y = py - cy
    rx = int(cx + x * c - y * s)
    ry = int(cy + x * s + y * c)
    return rx, ry


def draw_star_rot(display, cx, cy, size, angle, color=1):
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
    rpts = [rotated_point(x, y, cx, cy, angle) for x, y in pts]
    for i in range(len(rpts)):
        x1, y1 = rpts[i]
        x2, y2 = rpts[(i + 1) % len(rpts)]
        display.line(x1, y1, x2, y2, color)


def draw_grid_twinkle(display, frame, step=16, color=1):
    # simple deterministic 'twinkle' using frame
    for x in range(0, oled_width, step):
        for y in range(0, oled_height, 4):
            # pattern based on coordinates + frame to vary brightness
            if ((x // step) + (y // 4) + (frame // 3)) % 6 < 4:
                display.pixel(x, y, color)
    for y in range(0, oled_height, step):
        for x in range(0, oled_width, 4):
            if ((y // step) + (x // 4) + (frame // 4)) % 6 < 4:
                display.pixel(x, y, color)
    display.hline(0, center_y, oled_width, color)
    display.vline(center_x, 0, oled_height, color)


def clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


frame = 0
try:
    while True:
        oled.fill(0)
        draw_grid_twinkle(oled, frame)

        # pulsing circles
        r1 = 30 + int(6 * math.sin(frame * 0.12))
        r2 = 20 + int(4 * math.cos(frame * 0.15))
        r1 = clamp(r1, 4, 60)
        r2 = clamp(r2, 2, 50)
        draw_circle(oled, center_x, center_y, r1, 1)
        draw_circle(oled, center_x, center_y, r2, 1)

        # rotating star
        angle = frame * 0.18
        draw_star_rot(oled, center_x, center_y, 16, angle, 1)

        # orbiting sparkles
        for i in range(6):
            a = angle + i * (2 * math.pi / 6)
            orbit_r = r1 + 8 + (i % 2) * 6
            x = int(center_x + orbit_r * math.cos(a))
            y = int(center_y + orbit_r * math.sin(a))
            oled.pixel(x, y, 1)

        oled.show()
        time.sleep_ms(80)
        frame += 1
except KeyboardInterrupt:
    oled.fill(0)
    oled.show()
