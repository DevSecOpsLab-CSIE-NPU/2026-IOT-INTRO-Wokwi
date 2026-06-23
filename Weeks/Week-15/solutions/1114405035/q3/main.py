from machine import Pin, SPI, ADC, I2C
import ili9341
import ssd1306
import dht
import time
import network
import ujson
from umqtt.simple import MQTTClient
from fonts import draw_title

# ===== Parameters matching Student ID: 1114405035 =====
# DHT22 data pin: GPIO 23 (Units digit = 5)
# MQ2 AO pin: GPIO 34 (Tens digit = 3 -> mapped to 34)
# Alarm Threshold: 100 ppm (50 + 5 * 10 = 100 ppm)
# Title Color: Cyan (青) (Units digit = 5 -> range 3~5)
# OLED I2C pins: SCL = GPIO 22, SDA = GPIO 21
# ======================================================

WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
ACCESS_TOKEN = "VSSqHwJUIMetkEDA3Nga"
MQTT_PASS = "pzcgbajjh274h8jtri07"
TB_HOST = "thingsboard.cloud"

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

# === WiFi and MQTT Connection helper ===
def connect_wifi_mqtt():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    print("[WiFi] Connecting to", WIFI_SSID, "...")
    
    timeout = 15
    while not wlan.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1
    print()
    
    if wlan.isconnected():
        print("[WiFi] Connected! IP:", wlan.ifconfig()[0])
        try:
            client = MQTTClient(
                client_id=b"esp32_1114405035_q3",
                server=TB_HOST,
                port=1883,
                user=ACCESS_TOKEN,
                password=MQTT_PASS
            )
            client.connect()
            print("[MQTT] Connected to ThingsBoard!")
            return client
        except Exception as e:
            print("[MQTT] Connection failed:", e)
            return None
    else:
        print("[WiFi] Connection failed.")
        return None

# ==========================================
# STEP 1: Q1 Draw Title on ILI9341 TFT LCD
# ==========================================
print("=== Step 1: Draw Title on ILI9341 ===")
# CS=GPIO5, D/C=GPIO17, MOSI=GPIO23, SCK=GPIO18
spi = SPI(2, baudrate=40000000, sck=Pin(18), mosi=Pin(23))
dc = Pin(17, Pin.OUT)
cs = Pin(5, Pin.OUT)
display = ili9341.ILI9341(spi, cs=cs, dc=dc)

# Fill screen with black
display.fill(ili9341.color565(0, 0, 0))

# Cyan color (青) is color565(0, 255, 255)
CYAN = ili9341.color565(0, 255, 255)

# Center layout for 10 characters "大城北游泳池空汙偵測":
# 5 characters per row (2 rows total). Start x = (240 - 5 * 32) / 2 = 40. Start y = 20.
draw_title(display, x=40, y=20, color=CYAN, scale=1, per_row=5, gap_y=10)
print("[LCD] Title drawn successfully.")

# Deinitialize SPI and free Pin 23 to prevent electrical conflicts with DHT22
spi.deinit()
Pin(23, Pin.IN) # Reset Pin 23 to general input
time.sleep_ms(100)

# ==========================================
# STEP 2: Initialize SSD1306 OLED and Sensors
# ==========================================
print("=== Step 2: Initialize OLED and Sensors ===")
# OLED SDA = GPIO 21, SCL = GPIO 22
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# DHT22 on GPIO 23
dht22 = dht.DHT22(Pin(23))

# MQ2 AO on GPIO 34 (ADC)
gas_adc = ADC(Pin(34))
gas_adc.atten(ADC.ATTN_11DB) # Map voltage to 0~3.3V range

# Connect to cloud (WiFi & MQTT)
mqtt_client = connect_wifi_mqtt()

# OLED boot screen
oled.fill(0)
oled.text("Dacheng Monitor", 0, 10)
oled.text("Booting...", 0, 30)
oled.show()
time.sleep(1)

# ==========================================
# STEP 3: Main Loop (Update every 2 seconds)
# ==========================================
print("=== Step 3: Running Main Loop ===")
THRESHOLD = 100 # Alarm threshold (100 ppm)

while True:
    try:
        # Measure DHT22 Temperature & Humidity
        dht22.measure()
        t = dht22.temperature()
        h = dht22.humidity()
        
        # Read MQ2 Sensor
        raw = gas_adc.read()
        ppm = raw_to_ppm(raw)
        
        # OLED Display
        oled.fill(0)
        oled.text("Temp:  {:.1f} C".format(t), 0, 5)
        oled.text("Humid: {:.1f} %".format(h), 0, 25)
        
        # PPM Display & Alarm condition (Q3)
        if ppm >= THRESHOLD:
            oled.text("Gas:   {} ppm *AL*".format(ppm), 0, 45)
            print("[ALARM] gas_ppm ({}) exceeds threshold ({} ppm)!".format(ppm, THRESHOLD))
        else:
            oled.text("Gas:   {} ppm".format(ppm), 0, 45)
            
        oled.show()
        
        # Q2: Serial Debug Output
        print("[DEBUG] Temp: {:.1f} C, Humid: {:.1f} %, Gas: {} ppm (Raw: {})".format(t, h, ppm, raw))
        
        # Q3: Upload telemetry via MQTT
        if mqtt_client is not None:
            try:
                telemetry = ujson.dumps({
                    "temperature": t,
                    "humidity": h,
                    "gas_raw": raw,
                    "gas_ppm": ppm
                })
                mqtt_client.publish(b"v1/devices/me/telemetry", telemetry, qos=1)
                print("[MQTT] Uploaded telemetry:", telemetry)
            except Exception as e:
                print("[MQTT] Publish error, attempting reconnect:", e)
                try:
                    mqtt_client.connect()
                except Exception as rc:
                    print("[MQTT] Reconnect failed:", rc)
                    
    except Exception as e:
        print("[ERROR] Main Loop Exception:", e)
        
    time.sleep(5)
