import time
import network
import ujson
from machine import Pin, ADC
from umqtt.simple import MQTTClient

SSID = "Wokwi-GUEST"
PASSWORD = ""

MQTT_SERVER = "mqtt.thingsboard.cloud"
MQTT_PORT = 1883
ACCESS_TOKEN = "gqaq1HUIJUUb7BLWyuU3"
CLIENT_ID = "esp32-mq2-ppm"

THRESHOLD = 140

mq2 = ADC(Pin(35))
mq2.atten(ADC.ATTN_11DB)

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
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("[WIFI] connecting to {}...".format(SSID))
        wlan.connect(SSID, PASSWORD)
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
    if wlan.isconnected():
        print("[WIFI] connected, IP =", wlan.ifconfig()[0])
    else:
        print("[WIFI] connect failed, will retry later")
    return wlan


def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_SERVER, port=MQTT_PORT,
                         user=ACCESS_TOKEN, password="")
    client.connect()
    print("[MQTT] connected to {}:{}".format(MQTT_SERVER, MQTT_PORT))
    return client


wlan = connect_wifi()

client = None
while client is None:
    try:
        client = connect_mqtt()
    except Exception as e:
        print("[MQTT] connect failed:", e, "- retrying in 5s")
        time.sleep(5)

while True:
    if not wlan.isconnected():
        print("[WIFI] disconnected, reconnecting...")
        wlan = connect_wifi()

    raw = mq2.read()
    gas_ppm = raw_to_ppm(raw)
    payload = ujson.dumps({"gas_ppm": gas_ppm})

    try:
        client.publish("v1/devices/me/telemetry", payload, qos=1)
        if gas_ppm > THRESHOLD:
            print("[ALARM] gas_ppm={}".format(gas_ppm))
        else:
            print("[DEBUG] gas_ppm={}".format(gas_ppm))
    except Exception as e:
        print("[MQTT] publish failed:", e, "- reconnecting...")
        try:
            client = connect_mqtt()
        except Exception as e2:
            print("[MQTT] reconnect failed:", e2)

    time.sleep(5)
