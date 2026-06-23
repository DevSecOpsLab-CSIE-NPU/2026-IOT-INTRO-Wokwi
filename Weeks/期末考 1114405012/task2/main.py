from machine import Pin, I2C, ADC
import ssd1306
import dht
import time

TITLE = "Dacheng AirMon"
OLED_W = 128
OLED_H = 64

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


i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(OLED_W, OLED_H, i2c)

dht22 = dht.DHT22(Pin(16))
mq2 = ADC(Pin(35))
mq2.atten(ADC.ATTN_11DB)


def draw_frame(temp_c, humidity, ppm):
    oled.fill(0)
    oled.rect(0, 0, OLED_W, OLED_H, 1)
    oled.hline(0, 12, OLED_W, 1)
    oled.text(TITLE, 8, 2)
    oled.text("Temp: {:.1f} C".format(temp_c), 8, 20)
    oled.text("Humi: {:.1f} %".format(humidity), 8, 32)
    oled.text("Gas : {} ppm".format(ppm), 8, 44)
    oled.show()


while True:
    try:
        dht22.measure()
        temp_c = dht22.temperature()
        humidity = dht22.humidity()
        raw = mq2.read()
        ppm = raw_to_ppm(raw)

        print("[DEBUG] temperature = {:.1f}C, humidity = {:.1f}%, gas_raw={}, gas_ppm={}".format(
            temp_c, humidity, raw, ppm))

        draw_frame(temp_c, humidity, ppm)

    except Exception as exc:
        print("[ERROR]", exc)
        oled.fill(0)
        oled.text("Sensor Error", 8, 24)
        oled.show()

    time.sleep(2)
