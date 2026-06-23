from machine import Pin, ADC
from umqtt.simple import MQTTClient
import network
import ujson
import time


WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

HOST = "mqtt.thingsboard.cloud"
PORT = 1883
CLIENT_ID = "csie-npu"
USERNAME = "1114405040"
PASSWORD = "csie1114405040"
TOPIC = b"v1/devices/me/telemetry"

MQ2_GPIO = 32
ALARM_THRESHOLD = 50
SEND_INTERVAL = 5
MQ2_K = 2.54
MQ2_P = 2.467


def raw_to_ppm(raw):
    v = raw / 4095.0
    if v <= 0:
        return 0
    if v >= 1:
        v = 0.999
    ratio = v / (1.0 - v)
    ppm = int(MQ2_K * (ratio ** MQ2_P))
    return int((ppm + 5) // 10) * 10


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("[WiFi] Connecting to", WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            print("[WiFi] Waiting...")
            time.sleep(1)
    print("[WiFi] Connected:", wlan.ifconfig())
    return wlan


def connect_mqtt():
    client = MQTTClient(
        client_id=CLIENT_ID,
        server=HOST,
        port=PORT,
        user=USERNAME,
        password=PASSWORD,
        keepalive=60,
    )
    print("[MQTT] Connecting to {}:{} as {}".format(HOST, PORT, USERNAME))
    client.connect()
    print("[MQTT] Connected")
    return client


def publish_gas(client, ppm):
    payload = ujson.dumps({"gas_ppm": ppm})
    client.publish(TOPIC, payload)
    print("[MQTT] Published:", payload)


# diagram.json wiring: MQ2 AO -> GPIO32
mq2 = ADC(Pin(MQ2_GPIO))
mq2.atten(ADC.ATTN_11DB)

connect_wifi()
mqtt = connect_mqtt()

while True:
    raw = mq2.read()
    ppm = raw_to_ppm(raw)
    print("[DEBUG] gas_raw={} gas_ppm={}".format(raw, ppm))

    if ppm > ALARM_THRESHOLD:
        print("[ALARM] Gas concentration exceeded threshold")

    try:
        publish_gas(mqtt, ppm)
    except Exception as e:
        print("[MQTT] Publish failed:", e)
        try:
            mqtt.disconnect()
        except Exception:
            pass
        mqtt = connect_mqtt()

    time.sleep(SEND_INTERVAL)
