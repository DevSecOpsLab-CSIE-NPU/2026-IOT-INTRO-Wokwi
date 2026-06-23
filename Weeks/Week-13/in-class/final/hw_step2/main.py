# main.py - Step 2: 感測讀取與 OLED 顯示
from machine import Pin, I2C, ADC
import time
import dht
import ssd1306

DHT_PIN = 17
MQ2_PIN = 14

# OLED 初始化
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# 感測器初始化
dht22 = dht.DHT22(Pin(DHT_PIN))

mq2 = ADC(Pin(MQ2_PIN))
# 設定衰減，讓 ADC 可讀取 0~3.3V 全範圍
mq2.atten(ADC.ATTN_11DB)

# MQ2 換算公式（Week 15 非線性模型）
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


def update_oled(temp, humi, ppm):
    """每 2 秒更新一次 OLED 畫面（白字黑底）。"""
    oled.fill(0)
    oled.text("Dacheng AirMon", 0, 0)

    if temp is None:
        oled.text("Temp: N/A", 0, 16)
    else:
        oled.text("Temp: {:.1f} C".format(temp), 0, 16)

    if humi is None:
        oled.text("Humi: N/A", 0, 32)
    else:
        oled.text("Humi: {:.1f} %".format(humi), 0, 32)

    oled.text("Gas : {} ppm".format(ppm), 0, 48)
    oled.show()


while True:
    try:
        dht22.measure()
        temp = dht22.temperature()
        humi = dht22.humidity()
    except Exception as e:
        print("[ERROR] DHT22 read failed:", e)
        temp = None
        humi = None

    raw = mq2.read()
    ppm = raw_to_ppm(raw)

    update_oled(temp, humi, ppm)

    if temp is None or humi is None:
        print("[DEBUG] Temp=N/A, Humi=N/A, Raw={}, Gas={} ppm".format(raw, ppm))
    else:
        print("[DEBUG] Temp={:.1f} C, Humi={:.1f} %, Raw={}, Gas={} ppm".format(
            temp, humi, raw, ppm))

    time.sleep(2)
