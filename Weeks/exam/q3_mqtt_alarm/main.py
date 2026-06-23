from machine import Pin, ADC
import time
import network
import ujson
from umqtt.simple import MQTTClient


ACCESS_TOKEN = "PUT_YOUR_THINGSBOARD_ACCESS_TOKEN_HERE"

WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

MQTT_HOST = "mqtt.thingsboard.cloud"
MQTT_PORT = 1883
MQTT_TOPIC = b"v1/devices/me/telemetry"

MQ2_PIN = 34
THRESHOLD = 140
UPLOAD_INTERVAL_MS = 5000


def raw_to_ppm(raw):
    return int((raw / 4095) * 300)


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("[WiFi] Connecting to", WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            print("[WiFi] waiting...")
            time.sleep(1)

    print("[WiFi] Connected:", wlan.ifconfig())
    return wlan


def connect_mqtt():
    client = MQTTClient(
        client_id=b"q3-mqtt-alarm",
        server=MQTT_HOST,
        port=MQTT_PORT,
        user=ACCESS_TOKEN,
        password=ACCESS_TOKEN,
    )
    client.connect()
    print("[MQTT] Connected to {}:{}".format(MQTT_HOST, MQTT_PORT))
    return client


mq2 = ADC(Pin(34))
mq2.atten(ADC.ATTN_11DB)

connect_wifi()
mqtt_client = connect_mqtt()

last_upload = time.ticks_ms() - UPLOAD_INTERVAL_MS

while True:
    now = time.ticks_ms()

    if time.ticks_diff(now, last_upload) >= UPLOAD_INTERVAL_MS:
        last_upload = now

        raw = mq2.read()
        ppm = raw_to_ppm(raw)
        payload = ujson.dumps({"gas_ppm": ppm})

        print("[DEBUG] raw={} gas_ppm={} threshold={}".format(raw, ppm, THRESHOLD))

        if ppm > THRESHOLD:
            print("[ALARM] gas_ppm over threshold")
        else:
            print("[NORMAL] gas_ppm <= threshold")

        try:
            mqtt_client.publish(MQTT_TOPIC, payload)
            print("[MQTT] Published:", payload)
        except Exception as exc:
            print("[MQTT] Publish failed:", exc)
            mqtt_client = connect_mqtt()

    time.sleep_ms(100)
