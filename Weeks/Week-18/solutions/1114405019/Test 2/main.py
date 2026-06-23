import time
from machine import Pin, I2C, ADC
import dht
import ssd1306

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

dht22 = dht.DHT22(Pin(33))

mq2 = ADC(Pin(35))
mq2.atten(ADC.ATTN_11DB)

K = 2.60
P = 2.467


def raw_to_ppm(raw):
    v = raw / 4095.0
    if v >= 1.0:
        v = 0.999
    if v <= 0.0:
        return 0
    ratio = v / (1.0 - v)
    return int(K * (ratio ** P))


while True:
    dht22.measure()
    temp = dht22.temperature()
    humi = dht22.humidity()

    raw = mq2.read()
    gas_ppm = raw_to_ppm(raw)

    oled.fill(0)
    oled.text("Dacheng AirMon", 0, 0)
    oled.text("Temp: {:.1f} C".format(temp), 0, 20)
    oled.text("Humi: {:.1f} %".format(humi), 0, 32)
    oled.text("Gas : {} ppm".format(gas_ppm), 0, 44)
    oled.show()

    print("[DEBUG] temp={:.1f} humi={:.1f} gas_ppm={}".format(temp, humi, gas_ppm))

    time.sleep(2)
