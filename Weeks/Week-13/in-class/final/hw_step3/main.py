# main.py - Step 3: 雲端 PPM 告警 (MQTT -> ThingsBoard)
from machine import Pin, ADC
import time
import network
import ujson
from umqtt.simple import MQTTClient

MQ2_PIN = 34
THRESHOLD = 90          # ppm 告警門檻

# WiFi / MQTT 設定
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
ACCESS_TOKEN = "7jsfisdaeujc79kh3t5u"  # <-- 請填入 ThingsBoard 裝置 Token
TB_SERVER = "mqtt.thingsboard.cloud"
TB_PORT = 1883
TELEMETRY_TOPIC = "v1/devices/me/telemetry"

# MQ2 初始化
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


def connect_wifi():
    """連線至 Wokwi-GUEST（免密碼）。"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("[DEBUG] Connecting to WiFi:", WIFI_SSID)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    while not wlan.isconnected():
        time.sleep_ms(500)
    print("[DEBUG] WiFi connected, IP:", wlan.ifconfig()[0])
    return wlan


def connect_mqtt():
    """連線至 ThingsBoard MQTT broker。"""
    client = MQTTClient(
        client_id=b"wokwi",
        server=TB_SERVER,
        port=TB_PORT,
        user=ACCESS_TOKEN,
        password="",
        keepalive=60
    )
    client.connect()
    print("[DEBUG] MQTT connected to", TB_SERVER)
    return client


def publish_gas(client, ppm):
    """每 5 秒上傳 gas_ppm 至 ThingsBoard telemetry，qos=1。"""
    payload = ujson.dumps({"gas_ppm": ppm})
    client.publish(TELEMETRY_TOPIC, payload, qos=1)
    print("[DEBUG] MQTT publish:", payload)


# 連線網路與 MQTT
connect_wifi()
mqtt_client = connect_mqtt()

last_ms = 0
INTERVAL = 5000   # 5 秒

ppm = 0

while True:
    raw = mq2.read()
    ppm = raw_to_ppm(raw)

    print("[DEBUG] Raw={}, Gas={} ppm".format(raw, ppm))

    # 本地告警判斷
    if ppm > THRESHOLD:
        print("[ALARM] Gas {} ppm exceeds threshold {} ppm!".format(ppm, THRESHOLD))

    # 每 5 秒上傳一次
    now = time.ticks_ms()
    if time.ticks_diff(now, last_ms) >= INTERVAL:
        try:
            publish_gas(mqtt_client, ppm)
        except Exception as e:
            print("[ERROR] MQTT publish failed:", e)
            mqtt_client = connect_mqtt()
        last_ms = now

    time.sleep_ms(500)
