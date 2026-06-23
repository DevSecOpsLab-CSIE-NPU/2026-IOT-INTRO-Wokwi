from machine import Pin, I2C, ADC, SPI
import ili9341
import fonts
import ssd1306
import dht
import time


# Existing circuit pins in task2a/diagram.json
TFT_CS_PIN = 5
TFT_DC_PIN = 17
TFT_SCK_PIN = 18
TFT_MOSI_PIN = 23
OLED_SCL_PIN = 22
OLED_SDA_PIN = 21
DHT22_PIN = 17
MQ2_AO_PIN = 34

TFT_WIDTH = 240
TFT_HEIGHT = 320
TFT_CHAR_SIZE = 32
TFT_LINE_GAP = 12
TFT_TITLE_ROWS = ("\u5927\u57ce\u5317\u6e38\u6cf3", "\u6c60\u7a7a\u6c59\u5075\u6e2c")

OLED_WIDTH = 128
OLED_HEIGHT = 64
UPDATE_INTERVAL_SEC = 2

TFT_BLACK = ili9341.color565(0, 0, 0)
# Wokwi ILI9341 uses BGR ordering here, so this RGB565 value appears cyan.
TFT_CYAN = ili9341.color565(255, 255, 0)

FONT_ZHEN = (
    b"\x00\x04\x10\x00\x00\x04\x10\x00\x00\x04\x10\x00\x00\x02\xf0?"
    b"\x00\x02\x10\x00\x00\x01\x10\x00\x80\x00\x10\x00\x80\xe0\xff"
    b"\x0f\xc0 \x00\x08\xa0 \x00\x08\xb0 \x00\x08\x90 \x00\x08\x88"
    b"\xe0\xff\x0f\x80 \x00\x08\x80 \x00\x08\x80 \x00\x08\x80\xe0"
    b"\xff\x0f\x80 \x00\x08\x80 \x00\x08\x80 \x00\x08\x80 \x00\x08"
    b"\x80\xe0\xff\x0f\x80\x00\x00\x00\x80\x00\x83\x01\x80\x80\x00"
    b"\x06\x80`\x00\x08\x80\x18\x000\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
)
fonts.CHARS["\u5075"] = (FONT_ZHEN, 32, 32)


def draw_tft_char(display, ch, x, y, color):
    data, w, h = fonts.CHARS[ch]
    color_bytes = color.to_bytes(2, "big")
    buf = bytearray(w * h * 2)

    for sy in range(h):
        for sx in range(w):
            if data[sy * 4 + sx // 8] & (1 << (sx % 8)):
                i = (sy * w + sx) * 2
                buf[i] = color_bytes[0]
                buf[i + 1] = color_bytes[1]

    display._window_and_data(x, y, x + w - 1, y + h - 1, buf)


def show_tft_title():
    spi = SPI(2, baudrate=40_000_000, sck=Pin(TFT_SCK_PIN), mosi=Pin(TFT_MOSI_PIN))
    display = ili9341.ILI9341(spi, cs=Pin(TFT_CS_PIN, Pin.OUT), dc=Pin(TFT_DC_PIN, Pin.OUT))
    display.fill(TFT_BLACK)

    block_h = len(TFT_TITLE_ROWS) * TFT_CHAR_SIZE + (len(TFT_TITLE_ROWS) - 1) * TFT_LINE_GAP
    start_y = (TFT_HEIGHT - block_h) // 2

    for row, text in enumerate(TFT_TITLE_ROWS):
        x = (TFT_WIDTH - len(text) * TFT_CHAR_SIZE) // 2
        y = start_y + row * (TFT_CHAR_SIZE + TFT_LINE_GAP)

        for col, ch in enumerate(text):
            draw_tft_char(display, ch, x + col * TFT_CHAR_SIZE, y, TFT_CYAN)


# First question: keep the ILI9341 title screen.
# GPIO17 is shared by TFT D/C and DHT22 DATA in the existing circuit, so draw
# the TFT once first, then reinitialize GPIO17 for DHT22 below.
show_tft_title()


# Task 1: Initialize I2C and SSD1306 OLED.
i2c = I2C(0, scl=Pin(OLED_SCL_PIN), sda=Pin(OLED_SDA_PIN))
oled = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)


# Task 2: Initialize DHT22 and MQ2 sensors.
dht22 = dht.DHT22(Pin(DHT22_PIN))
mq2 = ADC(Pin(MQ2_AO_PIN))
mq2.atten(ADC.ATTN_11DB)


def mq2_raw_to_ppm(raw):
    """Convert MQ2 ADC value to approximate ppm with a non-linear curve."""
    v = raw / 4095.0

    if v <= 0:
        return 0
    if v >= 1.0:
        v = 0.999

    ratio = v / (1.0 - v)
    k = 2.60
    p = 2.467
    return int(k * (ratio ** p))


def show_readings(temp, humi, gas_ppm):
    oled.fill(0)
    oled.text("Dacheng AirMon", 0, 0)
    oled.text("Temp: {:.1f} C".format(temp), 0, 16)
    oled.text("Humi: {:.1f} %".format(humi), 0, 32)
    oled.text("Gas : {} ppm".format(gas_ppm), 0, 48)
    oled.show()


def show_error(err):
    oled.fill(0)
    oled.text("Dacheng AirMon", 0, 0)
    oled.text("Sensor Error", 0, 24)
    oled.text(str(err)[:16], 0, 40)
    oled.show()


while True:
    try:
        # Task 3: Read and process DHT22 + MQ2 data.
        dht22.measure()
        temperature = dht22.temperature()
        humidity = dht22.humidity()

        gas_raw = mq2.read()
        gas_ppm = mq2_raw_to_ppm(gas_raw)

        # Task 4: Refresh OLED display every 2 seconds.
        show_readings(temperature, humidity, gas_ppm)

        # Task 5: Serial debug log.
        print(
            "[DEBUG] Temp: {:.1f} C, Humi: {:.1f} %, Gas raw: {}, Gas ppm: {}".format(
                temperature, humidity, gas_raw, gas_ppm
            )
        )

    except Exception as err:
        show_error(err)
        print("[DEBUG] Sensor Error:", err)

    time.sleep(UPDATE_INTERVAL_SEC)
