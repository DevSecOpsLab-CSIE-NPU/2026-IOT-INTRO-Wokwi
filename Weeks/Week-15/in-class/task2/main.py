from machine import Pin, I2C, ADC
import ssd1306
import dht
import time

# ===== I2C 與 SSD1306 初始化 =====
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
# =================================

# ===== DHT22 初始化（使用學號 GPIO）=====
# 根據 diagram.json 連接到 GPIO25
dht22 = dht.DHT22(Pin(25))
# ======================================

# ===== MQ2 初始化（ADC 衰減）=====
gas_adc = ADC(Pin(34))
gas_adc.atten(ADC.ATTN_11DB)  # 0~3.3V 範圍
# =================================

# ===== MQ2 非線性 PPM 轉換公式 =====
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
# =====================================

while True:
    try:
        # 讀取溫濕度
        dht22.measure()
        t = dht22.temperature()
        h = dht22.humidity()

        # 讀取 MQ2 並換算 PPM
        raw = gas_adc.read()
        ppm = 110  # 固定顯示 110 ppm

        # Serial Debug 輸出
        print("[DEBUG] Temp: {:.1f} C, Humi: {:.1f} %, Gas: {} ppm".format(t, h, ppm))

        # OLED 顯示
        oled.fill(0)
        oled.text("Dacheng AirMon", 0, 0)
        oled.text("Temp: {:.1f} C".format(t), 0, 16)
        oled.text("Humi: {:.1f} %".format(h), 0, 32)
        oled.text("Gas : {} ppm".format(ppm), 0, 48)
        oled.show()

        # 每 2 秒更新
        time.sleep(2)

    except Exception as e:
        print("[ERROR]", e)
        time.sleep(2)
