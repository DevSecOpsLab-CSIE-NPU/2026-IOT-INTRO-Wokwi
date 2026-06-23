import network
import time
import ujson
from machine import Pin, ADC
from umqtt.simple import MQTTClient

WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

TB_HOST = "mqtt.thingsboard.cloud"
TB_PORT = 1883

# 你的最新 mosquitto_pub 测试凭证
CLIENT_ID = "0psszq22h3mdayuotac2"
USERNAME = "3bh9y66fg6mlc7t94g9q"
PASSWORD = "q0javgni8e3zt37u0tkj"

gas_adc = ADC(Pin(4))
gas_adc.atten(ADC.ATTN_11DB)

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

topic = b"v1/devices/me/telemetry"

def connect_mqtt():
    global client
    try:
        client = MQTTClient(
            client_id=CLIENT_ID.encode(),
            server=TB_HOST,
            port=TB_PORT,
            user=USERNAME.encode(),
            password=PASSWORD.encode()
        )
        client.connect()
        print("✅ Connected to ThingsBoard")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)
print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep_ms(500)
print("WiFi connected:", wifi.ifconfig())

print("Connecting to ThingsBoard...")
client = None
if not connect_mqtt():
    print("Initial connection failed, will retry...")

while True:
    if client is None or not hasattr(client, '_sock'):
        print("MQTT连接丢失，重新连接...")
        if not connect_mqtt():
            time.sleep(5)
            continue

    try:
        raw = gas_adc.read()
        ppm = raw_to_ppm(raw)
        print("[DEBUG] raw={} gas={}ppm".format(raw, ppm))

        telemetry = ujson.dumps({"gas_ppm": ppm})
        client.publish(topic, telemetry)
        print("✅ Published to ThingsBoard:", telemetry)

    except Exception as e:
        print(f"❌ Publish failed: {e}")
        client = None

    time.sleep(5)
