from machine import Pin, ADC
import network
import time
import ujson
from umqtt.simple import MQTTClient

# 學號末兩碼：23
MQ2_PIN = 34
THRESHOLD = 80       # 50 + 個位數 3 * 10 = 80 ppm

# Wokwi WiFi
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

# ThingsBoard MQTT
TB_HOST = "mqtt.thingsboard.cloud"
TB_PORT = 1883
TB_TOPIC = b"v1/devices/me/telemetry"

# Access Token 模式：把 Device 的 Access Token 填到 TB_USERNAME，TB_PASSWORD 留空。
# 如果你的裝置使用 MQTT Basic credentials，則 username/password 都要填。
TB_USERNAME = "did5libd87fni24vzbsd"
TB_PASSWORD = ""
CLIENT_ID = "d14405023-mq2"

PUBLISH_INTERVAL_MS = 5000

# MQ2 ppm 校正參數：參考 Week-15 的非線性模型
K = 2.60
P = 2.467


def to_bytes(value):
    if value is None:
        return None
    if isinstance(value, bytes):
        return value
    return value.encode()


def raw_to_ppm(raw):
    v = raw / 4095.0
    if v >= 1.0:
        v = 0.999
    if v <= 0.0:
        return 0
    ratio = v / (1.0 - v)
    return int(K * (ratio ** P))


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("[WiFi] Connecting to {} ...".format(WIFI_SSID))
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep_ms(500)
            print(".", end="")
        print()

    print("[WiFi] Connected:", wlan.ifconfig())
    return wlan


def connect_mqtt():
    username = TB_USERNAME
    password = TB_PASSWORD

    if username == "PUT_YOUR_ACCESS_TOKEN_HERE":
        print("[WARN] Please fill TB_USERNAME with your ThingsBoard Access Token first.")

    client = MQTTClient(
        client_id=to_bytes(CLIENT_ID),
        server=TB_HOST,
        port=TB_PORT,
        user=to_bytes(username),
        password=to_bytes(password),
        keepalive=60,
    )
    print("[MQTT] Connecting to {}:{} ...".format(TB_HOST, TB_PORT))
    client.connect()
    print("[MQTT] Connected")
    return client


# MQ2 ADC 初始化
gas_adc = ADC(Pin(MQ2_PIN))
gas_adc.atten(ADC.ATTN_11DB)

connect_wifi()
client = None
last_publish = time.ticks_ms() - PUBLISH_INTERVAL_MS

while True:
    try:
        if client is None:
            client = connect_mqtt()

        raw = gas_adc.read()
        ppm = raw_to_ppm(raw)

        now = time.ticks_ms()
        if time.ticks_diff(now, last_publish) >= PUBLISH_INTERVAL_MS:
            last_publish = now

            payload = ujson.dumps({"gas_ppm": ppm})
            client.publish(TB_TOPIC, payload, qos=1)
            print("[MQTT] publish", payload)

            if ppm > THRESHOLD:
                print("[ALARM] gas_ppm={} > THRESHOLD={} ppm".format(ppm, THRESHOLD))
            else:
                print("[OK] gas_ppm={} <= THRESHOLD={} ppm".format(ppm, THRESHOLD))

        time.sleep_ms(200)

    except Exception as e:
        print("[ERROR]", e)
        try:
            if client:
                client.disconnect()
        except Exception:
            pass
        client = None
        time.sleep(3)
