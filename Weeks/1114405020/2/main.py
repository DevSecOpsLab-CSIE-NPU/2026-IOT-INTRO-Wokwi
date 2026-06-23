from machine import Pin, I2C, ADC
import dht
import ssd1306
import time

# 學號尾碼 20 → DHT22(Pin4), MQ2(Pin26)；I2C fixed: SCL=22, SDA=21
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

dht22 = dht.DHT22(Pin(4))
gas_adc = ADC(Pin(26))
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
        ppm = raw_to_ppm(gas_adc.read())

        oled.fill(0)
        oled.text("Dacheng AirMon", 0, 0)
        oled.text("Temp: {:.1f} C".format(t), 0, 16)
        oled.text("Humi: {:.1f} %".format(h), 0, 32)
        oled.text("Gas : {} ppm".format(ppm), 0, 48)
        oled.show()

        print("[DEBUG] Temp={:.1f}C Humi={:.1f}% Gas={}ppm".format(t, h, ppm))

    except Exception as e:
        print("[ERROR]", e)

    time.sleep(2)
