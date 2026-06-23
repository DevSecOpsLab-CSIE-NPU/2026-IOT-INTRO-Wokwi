from machine import Pin, ADC, I2C
import ssd1306
import dht
import time

# ===== Parameters matching Student ID: 1114405035 =====
# DHT22 data pin: GPIO 23 (Units digit = 5)
# MQ2 AO pin: GPIO 39 (Tens digit = 3)
# OLED I2C pins: SCL = GPIO 22, SDA = GPIO 21
# ======================================================

# Non-linear MQ2 calibration parameters (standard power model)
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

# Initialize SSD1306 OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize DHT22 sensor
dht22 = dht.DHT22(Pin(23))

# Initialize MQ2 AO (ADC)
gas_adc = ADC(Pin(39))
gas_adc.atten(ADC.ATTN_11DB) # 0~3.3V range

print("=== Q2: Sensing & OLED Display Loop Started ===")

while True:
    try:
        # Read temperature and humidity
        dht22.measure()
        t = dht22.temperature()
        h = dht22.humidity()
        
        # Read gas raw ADC and convert to ppm
        raw = gas_adc.read()
        ppm = raw_to_ppm(raw)
        
        # Display on OLED
        oled.fill(0)
        oled.text("Temp:  {:.1f} C".format(t), 0, 10)
        oled.text("Humid: {:.1f} %".format(h), 0, 30)
        oled.text("Gas:   {} ppm".format(ppm), 0, 50)
        oled.show()
        
        # Serial Console Debug Output (as required by Q2)
        print("[DEBUG] Temp: {:.1f} C, Humid: {:.1f} %, Gas: {} ppm (Raw: {})".format(t, h, ppm, raw))
        
    except Exception as e:
        print("[ERROR] Sensor reading error:", e)
        
    time.sleep(2)
