from machine import Pin, I2C
import sh1107

# ESP32 I2C pin assignment for Grove SH1107 OLED (match diagram.json wiring)
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

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


oled.fill(0)
draw_grid(oled, center_x, center_y, oled_width, oled_height)
draw_circle(oled, center_x, center_y, 35, 1)
draw_circle(oled, center_x, center_y, 32, 1)
draw_star(oled, center_x, center_y, 13, 1)
oled.show()
