from machine import ADC, I2C, Pin

import dht
import ssd1306
import time


print("Task2 main.py started")

OLED_WIDTH = 128
OLED_HEIGHT = 64

DHT_PIN = 19
MQ2_PIN = 35

MQ2_K = 2.60
MQ2_P = 2.467


def raw_to_ppm(raw):
    v = raw / 4095.0
    if v <= 0.0:
        return 0
    if v >= 1.0:
        v = 0.999
    ratio = v / (1.0 - v)
    return int(MQ2_K * (ratio ** MQ2_P))


def draw_values(temp, humi, gas_ppm):
    oled.fill(0)
    oled.text("Dacheng AirMon", 0, 0)
    oled.text("Temp: {:.1f} C".format(temp), 0, 16)
    oled.text("Humi: {:.1f} %".format(humi), 0, 30)
    oled.text("Gas : {} ppm".format(gas_ppm), 0, 44)
    oled.show()


i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)

dht22 = dht.DHT22(Pin(DHT_PIN))

gas_adc = ADC(Pin(MQ2_PIN))
gas_adc.atten(ADC.ATTN_11DB)


while True:
    try:
        dht22.measure()
        temp = dht22.temperature()
        humi = dht22.humidity()
        gas_ppm = raw_to_ppm(gas_adc.read())

        draw_values(temp, humi, gas_ppm)
        print("[DEBUG] temp={:.1f} humi={:.1f} gas={} ppm".format(temp, humi, gas_ppm))
    except Exception as e:
        oled.fill(0)
        oled.text("Dacheng AirMon", 0, 0)
        oled.text("Sensor error", 0, 24)
        oled.show()
        print("[ERROR] sensor read failed:", e)

    time.sleep(2)
