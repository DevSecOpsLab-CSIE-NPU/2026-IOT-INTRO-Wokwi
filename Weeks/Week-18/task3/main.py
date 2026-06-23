import time
import math
import network
import ujson
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# =====================================================================
# 1. 參數與學號專屬門檻設定 (完全對齊最新 MQTT Basic 憑證)
# =====================================================================
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

MQTT_SERVER = "mqtt.thingsboard.cloud"
MQTT_PORT = 1883

# 🛠️ 加上 Client ID 並填入你的最新帳密，徹底解決 MQTTException: 5
MQTT_CLIENT_ID = "a0n0udmto6e0ksvz8qjt"
MQTT_USER      = "cawkns0hn6h5sfpink15"
MQTT_PASSWORD  = "2ekgkgum08enc9w2swt0"

THRESHOLD = 60  # 您的學號專屬告警門檻：60 ppm

# MQ2 非線性校正係數 (完美沿用第二題高分成果)
MQ2_K = 2.60
MQ2_P = 2.467

# =====================================================================
# 2. 硬體初始化 (沿用第二題硬體，僅抓取第三題必要的 MQ2 ➔ GPIO 35)
# =====================================================================
mq2_adc = ADC(Pin(35))
mq2_adc.atten(ADC.ATTN_11DB) # 4095 滿量程

def raw_to_ppm(raw):
    v = raw / 4095.0
    if v >= 1.0: v = 0.999
    if v <= 0.0: return 0
    ratio = v / (1.0 - v)
    ppm = int(MQ2_K * (ratio ** MQ2_P))
    if ppm < 0: return 0
    if ppm > 1000: return 1000
    return ppm

# =====================================================================
# ⭐ 開機安全緩衝：留給 wokwi_run 腳本充足的連線時間，避免 RuntimeError
# =====================================================================
print("等待 Wokwi 腳本與網路初始化...")
time.sleep(3)

# =====================================================================
# 3. 連接 WiFi 與 ThingsBoard MQTT (使用完整授權驗證)
# =====================================================================
print("正在連接 WiFi...", end="")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.5)
print("\nWiFi 連線成功！IP:", wlan.ifconfig()[0])

print("正在連接 ThingsBoard MQTT...", end="")
# 💡 重點：在此處帶入指定的 MQTT_CLIENT_ID，完成完整權限認證
client = MQTTClient(
    client_id=MQTT_CLIENT_ID, 
    server=MQTT_SERVER, 
    port=MQTT_PORT, 
    user=MQTT_USER, 
    password=MQTT_PASSWORD,
    keepalive=60
)
client.connect()
print("MQTT 連線成功！")

# =====================================================================
# 4. 主循環：每 5 秒讀取、判斷告警、上傳雲端
# =====================================================================
while True:
    try:
        # 4.1 讀取數據並用非線性公式精準換算
        raw_val = mq2_adc.read()
        ppm = raw_to_ppm(raw_val)
        
        # 4.2 建立符合考卷要求的 JSON 酬載格式
        payload = {"gas_ppm": ppm}
        payload_str = ujson.dumps(payload)
        
        # 4.3 根據門檻值進行本地時印告警 (符合考卷提示 4 規格)
        if ppm > THRESHOLD:
            print("[ALARM] 警告！目前氣體濃度超標！目前: {} ppm (門檻: {} ppm)".format(ppm, THRESHOLD))
        else:
            print("[DEBUG] 目前空氣品質正常: {} ppm".format(ppm))
            
        # 4.4 上傳 Telemetry 至雲端 (Topic 固定為 v1/devices/me/telemetry, qos=1)
        client.publish("v1/devices/me/telemetry", payload_str, qos=1)
        print(" -> telemetry 已成功上傳至 ThingsBoard Cloud")

    except Exception as e:
        print("[ERROR] 發生異常中斷:", e)
        # 斷線自動重連機制
        try:
            client.connect()
        except:
            pass
            
    time.sleep(5) # 考卷規定每 5 秒上傳一次