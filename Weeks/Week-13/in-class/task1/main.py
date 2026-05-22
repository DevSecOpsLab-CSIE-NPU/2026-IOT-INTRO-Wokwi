from machine import Pin, I2C
import ssd1306

# ESP32 I2C pin assignment for SSD1306
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Dragon Ball inspired style tags shown on OLED
oled.fill(0)
oled.text("Hello, August!", 16, 28)
oled.show()
