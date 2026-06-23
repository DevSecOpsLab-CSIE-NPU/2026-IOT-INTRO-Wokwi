from machine import Pin, I2C, ADC
import dht
import ssd1306
import time

# 學號末兩碼：23
DHT_PIN = 19       # 個位數 3 -> GPIO19
MQ2_PIN = 34       # 十位數 2 -> GPIO34

# OLED I2C 固定腳位
I2C_SCL = 22
I2C_SDA = 21
OLED_W = 128
OLED_H = 64

# MQ2 ppm 校正參數：參考 Week-15 的非線性模型
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


# 初始化 OLED
# 注意：I2C 腳位不要跟 DHT22 / MQ2 重複
i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
oled = ssd1306.SSD1306_I2C(OLED_W, OLED_H, i2c)

# 初始化 DHT22 與 MQ2
dht22 = dht.DHT22(Pin(DHT_PIN))
gas_adc = ADC(Pin(MQ2_PIN))
gas_adc.atten(ADC.ATTN_11DB)


def show_values(temp, humi, ppm):
    oled.fill(0)
    oled.text("Dacheng AirMon", 0, 0)
    oled.text("Temp: {:.1f} C".format(temp), 0, 16)
    oled.text("Humi: {:.1f} %".format(humi), 0, 28)
    oled.text("Gas : {} ppm".format(ppm), 0, 40)
    oled.show()


while True:
    try:
        dht22.measure()
        temp = dht22.temperature()
        humi = dht22.humidity()

        raw = gas_adc.read()
        ppm = raw_to_ppm(raw)

        show_values(temp, humi, ppm)
        print("[DEBUG] Temp={:.1f}C Humi={:.1f}% raw={} Gas={}ppm".format(temp, humi, raw, ppm))

    except Exception as e:
        oled.fill(0)
        oled.text("Sensor Error", 0, 0)
        oled.text(str(e)[:16], 0, 16)
        oled.show()
        print("[ERROR]", e)

    time.sleep(2)
