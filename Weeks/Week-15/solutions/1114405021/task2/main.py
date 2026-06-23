from machine import Pin, I2C, ADC
import ssd1306
import dht
import time

# MQ2 非線性模型參數
K = 2.60
P = 2.467


def raw_to_ppm(raw):
    v = raw / 4095
    if v >= 1:
        v = 0.999
    if v <= 0:
        return 0
    return int(K * (v / (1 - v)) ** P)


# I2C OLED (SSD1306, 128x64)
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# DHT22 (學號末兩碼 21 → 個位 1 → GPIO 13)
dht22 = dht.DHT22(Pin(13))

# MQ2 (學號末兩碼 21 → 十位 2 → GPIO 36 ADC)
gas_adc = ADC(Pin(36))
gas_adc.atten(ADC.ATTN_11DB)

while True:
    try:
        dht22.measure()
        t = dht22.temperature()
        h = dht22.humidity()

        raw = gas_adc.read()
        ppm = raw_to_ppm(raw)

        print("[DEBUG] t={:.1f}C h={:.1f}% raw={} gas={}ppm".format(t, h, raw, ppm))

        oled.fill(0)
        oled.text("Dacheng AirMon", 0, 0)
        oled.text("Temp: {:.1f} C".format(t), 0, 16)
        oled.text("Humi: {:.1f} %".format(h), 0, 28)
        oled.text("Gas : {} ppm".format(ppm), 0, 40)
        oled.show()

    except Exception as e:
        print("[ERROR]", e)

    time.sleep(2)
