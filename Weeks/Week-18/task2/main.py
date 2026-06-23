import time
from machine import Pin, SPI, I2C, ADC
from ili9341 import ILI9341, color565
from fonts import draw_title
from ssd1306 import SSD1306_I2C
import dht

# =====================================================================
# 1. TFT 彩屏初始化 (維持 Task 1 成果，黃色標題不閃爍)
# =====================================================================
spi = SPI(1, baudrate=20_000_000, sck=Pin(18), mosi=Pin(23))
display = ILI9341(spi, cs=Pin(5, Pin.OUT), dc=Pin(17, Pin.OUT))

YELLOW = color565(0, 255, 255)  # 色彩反轉校正後的黃色
BLACK = color565(0, 0, 0)

display.fill(BLACK)
draw_title(display, x=40, y=120, color=YELLOW, scale=1) # 完美置中位置

# =====================================================================
# 2. OLED 與感測器初始化 (完全對齊 oled1, dht1, gas1 腳位)
# =====================================================================
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 64, i2c)

dht_sensor = dht.DHT22(Pin(13))

mq2_adc = ADC(Pin(35))
mq2_adc.atten(ADC.ATTN_11DB) # 設定 0~3.6V 量程 (4095 滿量程)

# MQ2 非線性校正係數（PPM = K * (v/(1-v))^P）
MQ2_K = 2.60
MQ2_P = 2.467


def raw_to_ppm(raw):
    v = raw / 4095.0
    if v >= 1.0:
        v = 0.999
    if v <= 0.0:
        return 0

    ratio = v / (1.0 - v)
    ppm = int(MQ2_K * (ratio ** MQ2_P))
    if ppm < 0:
        return 0
    if ppm > 1000:
        return 1000
    return ppm

# =====================================================================
# ⭐ 開機緩衝：延遲 3 秒，留給 wokwi_run 腳本腳步握手時間
# =====================================================================
print("硬體就緒，等待 Wokwi 序列埠完全連線...")
time.sleep(3)

# =====================================================================
# 3. 主循環：每 2 秒讀取並局部刷新 OLED
# =====================================================================
while True:
    try:
        # 3.1 讀取溫濕度數據
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        
        # 3.2 讀取氣體並用 MQ2 非線性公式換算 PPM
        raw_val = mq2_adc.read()
        ppm = raw_to_ppm(raw_val)

        # 3.3 OLED 顯示排版 (完全符合考卷「四、預期顯示」的外框與格式)
        oled.fill(0) # 清除 OLED 緩衝
        oled.text("+-------------------+", 0, 0)
        oled.text("| Dacheng AirMon    |", 0, 12)
        oled.text("| Temp: {:.1f} C     |".format(temp), 0, 24)
        oled.text("| Humi: {:.1f} %     |".format(hum), 0, 36)
        oled.text("| Gas : {} ppm     |".format(ppm), 0, 48)
        oled.text("+-------------------+", 0, 56)
        oled.show() # 將緩衝更新至 OLED 畫面

        # 3.4 Serial 印出 debug
        print("[DEBUG] Temp: {:.1f}C, Humi: {:.1f}%, Gas: {} ppm (Raw: {})".format(temp, hum, ppm, raw_val))

    except Exception as e:
        print("[ERROR] 讀取感測器失敗:", e)
        
    time.sleep(2) # 考卷規定每 2 秒更新一次