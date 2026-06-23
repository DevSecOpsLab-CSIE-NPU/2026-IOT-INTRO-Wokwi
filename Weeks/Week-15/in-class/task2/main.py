from machine import Pin, I2C, ADC
import ssd1306
import dht
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

dht22 = dht.DHT22(Pin(19))

gas_adc = ADC(Pin(34))
gas_adc.atten(ADC.ATTN_11DB)

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
    try:
        dht22.measure()
        t = dht22.temperature()
        h = dht22.humidity()
        raw = gas_adc.read()
        ppm = raw_to_ppm(raw)

        print("[DEBUG] t={:.1f}C h={:.1f}% raw={} gas={}ppm".format(t, h, raw, ppm))

        oled.fill(0)
        oled.text("Dacheng AirMon", 8, 0)
        oled.text("Temp: {:.1f} C".format(t), 0, 20)
        oled.text("Humi: {:.1f} %".format(h), 0, 36)
        oled.text("Gas : {} ppm".format(ppm), 0, 52)
        oled.show()

    except Exception as e:
        print("[ERROR]", e)

    time.sleep(2)
