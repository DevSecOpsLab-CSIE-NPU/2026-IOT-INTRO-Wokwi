import network
import time
import ujson
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# ===== 學號參數（末兩碼 21）=====
# MQ2 AO = GPIO36 (十位 2)
# THRESHOLD = 50 + 個位(1)*10 = 60 ppm
MQ2_PIN = 36
THRESHOLD = 60

# ===== ThingsBoard 設定 =====
# 從 mosquitto_pub 指令取得的認證
ACCESS_TOKEN = "dyjtln0h4c7zewaa2kyi"
TB_PASSWORD = "5dqhmiw2g1uyjvxm6jm7"
TB_HOST = "mqtt.thingsboard.cloud"
TB_PORT = 1883
CLIENT_ID = b"28qda086j5ibamiekmet"

# ===== MQ2 非線性模型參數 =====
K = 2.60
P = 2.467


def raw_to_ppm(raw):
    v = raw / 4095
    if v >= 1:
        v = 0.999
    if v <= 0:
        return 0
    return int(K * (v / (1 - v)) ** P)


# ===== 初始化 MQ2 =====
gas_adc = ADC(Pin(MQ2_PIN))
gas_adc.atten(ADC.ATTN_11DB)

# ===== 連線 WiFi (Wokwi-GUEST) =====
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("Wokwi-GUEST", "")

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(0.5)
print("WiFi connected:", wifi.ifconfig())

# ===== 連線 MQTT (ThingsBoard) =====
client = MQTTClient(
    client_id=CLIENT_ID,
    server=TB_HOST,
    port=TB_PORT,
    user=ACCESS_TOKEN,
    password=TB_PASSWORD,
)

print("Connecting to ThingsBoard...")
client.connect()
print("MQTT connected!")

# ===== 主迴圈：每 5 秒上傳一次 =====
while True:
    try:
        raw = gas_adc.read()
        ppm = raw_to_ppm(raw)

        # 本地印出
        print("[DEBUG] raw={} gas={}ppm".format(raw, ppm))
        if ppm > THRESHOLD:
            print("[ALARM] gas_ppm={} exceeds threshold {}!".format(ppm, THRESHOLD))

        # 上傳 telemetry 到 ThingsBoard
        payload = ujson.dumps({"gas_ppm": ppm})
        client.publish(b"v1/devices/me/telemetry", payload, qos=1)
        print("[MQTT] Published:", payload)

    except Exception as e:
        print("[ERROR]", e)
        # 嘗試重連
        try:
            client.connect()
            print("MQTT reconnected!")
        except:
            pass

    time.sleep(5)
