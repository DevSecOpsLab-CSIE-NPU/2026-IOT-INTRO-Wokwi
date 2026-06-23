from machine import Pin, I2C, ADC
import ssd1306
import dht
import time

# --- Configuration (adjust according to your diagram / 學號對照表) ---
# I2C for OLED (SSD1306) — matches diagram.json
I2C_SCL = 22
I2C_SDA = 21

# DHT22 data pin — match diagram (dht1:SDA -> esp:26)
DHT_PIN = 26

# MQ2 analog pin (ADC) — match diagram (gas1:AOUT -> esp:35)
MQ2_ADC_PIN = 35

# Simple MQ2 linear mapping: ADC (0-4095) -> 0..300 ppm (adjust as needed)
MQ2_PPM_MAX = 300

# --- Init hardware ---
i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

dht22 = dht.DHT22(Pin(DHT_PIN))
adc = ADC(Pin(MQ2_ADC_PIN))
adc.atten(ADC.ATTN_11DB)

def mq2_adc_to_ppm(adc_val):
    # adc_val: 0..4095 -> ppm: 0..MQ2_PPM_MAX
    return int(adc_val / 4095 * MQ2_PPM_MAX)

def draw_display(temp, hum, ppm):
    oled.fill(0)
    oled.text('Dacheng AirMon', 0, 0)
    oled.text('Temp: {:.1f} C'.format(temp), 0, 16)
    oled.text('Humi: {:.1f} %'.format(hum), 0, 28)
    oled.text('Gas : {} ppm'.format(ppm), 0, 40)
    oled.text('Serial: debug', 0, 56)
    oled.show()

print('[INFO] starting sensor loop')
while True:
    try:
        dht22.measure()
        t = dht22.temperature()
        h = dht22.humidity()
        a = adc.read()
        ppm = mq2_adc_to_ppm(a)
        print('[DEBUG] T={:.1f}C H={:.1f}% ADC={} PPM={}'.format(t, h, a, ppm))
        draw_display(t, h, ppm)
    except Exception as e:
        print('[ERROR]', e)
        oled.fill(0)
        oled.text('Sensor Error', 0, 0)
        oled.text(str(e), 0, 16)
        oled.show()
    time.sleep(2)
