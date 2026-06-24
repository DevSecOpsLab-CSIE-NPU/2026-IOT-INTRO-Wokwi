from machine import Pin, I2C, ADC
import ssd1306
import dht
import time

# Configuration for student 1114405022
DHT_PIN = 16
MQ2_PIN = 34
SCL_PIN = 22
SDA_PIN = 21

# MQ2 Non-linear model constants
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

# Initialize I2C and OLED
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize Sensors
dht_sensor = dht.DHT22(Pin(DHT_PIN))
mq2_adc = ADC(Pin(MQ2_PIN))
mq2_adc.atten(ADC.ATTN_11DB)

def format_line(content):
    if len(content) < 14:
        content = content + " " * (14 - len(content))
    elif len(content) > 14:
        content = content[:14]
    return "|" + content + "|"

def update_display(temp, humi, ppm):
    oled.fill(0)
    oled.text("+--------------+", 0, 0)
    oled.text(format_line("Dacheng AirMon"), 0, 10)
    oled.text(format_line("Temp: {:.1f} C".format(temp)), 0, 21)
    oled.text(format_line("Humi: {:.1f} %".format(humi)), 0, 32)
    oled.text(format_line("Gas : {} ppm".format(ppm)), 0, 43)
    oled.text("+--------------+", 0, 54)
    oled.show()

print("Starting sensor readings...")

while True:
    try:
        dht_sensor.measure()
        t = dht_sensor.temperature()
        h = dht_sensor.humidity()
        raw = mq2_adc.read()
        ppm = raw_to_ppm(raw)
        update_display(t, h, ppm)
        print("Temp: {:.1f}C, Humi: {:.1f}%, Gas: {}ppm".format(t, h, ppm))
    except Exception as e:
        print("Error reading sensors:", e)
    time.sleep(2)
