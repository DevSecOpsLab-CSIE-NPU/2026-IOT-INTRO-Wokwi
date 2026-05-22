
from machine import Pin, I2C
import ssd1306
import time

# ESP32 I2C pin assignment for SSD1306
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


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


def main():
	x = 16
	y = 32
	vx = 2
	radius = 10

	while True:
		oled.fill(0)
		draw_circle(oled, x, y, radius, 1)
		oled.text('Moving', 2, 2)
		oled.text('Circle', 2, 12)
		oled.show()

		x += vx
		if x - radius <= 0 or x + radius >= oled_width:
			vx = -vx
		time.sleep_ms(60)


if __name__ == '__main__':
	main()