from machine import Pin, ADC
import network
import time
import ujson
from umqtt.simple import MQTTClient

# Configuration for student 1114405022
MQ2_PIN = 34
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
TB_HOST = "thingsboard.cloud"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE" 

# MQ2 Non-linear model constants
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

# Initialize MQ2
mq2_adc = ADC(Pin(MQ2_PIN))
mq2_adc.atten(ADC.ATTN_11DB)
THRESHOLD = 70

def connect_wifi():
    print("Connecting to WiFi...", end="")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\nConnected!")

def connect_mqtt():
    print("Connecting to MQTT...", end="")
    client = MQTTClient(client_id="esp32_mq2",
                        server=TB_HOST,
                        port=1883,
                        user=ACCESS_TOKEN,
                        password="")
    client.connect()
    print("\nConnected!")
    return client

connect_wifi()
mqtt_client = connect_mqtt()

print("Starting gas monitoring...")

while True:
    try:
        raw = mq2_adc.read()
        ppm = raw_to_ppm(raw)
        payload = ujson.dumps({"gas_ppm": ppm})
        mqtt_client.publish("v1/devices/me/telemetry", payload, qos=1)
        print("Published: {} (PPM: {})".format(payload, ppm))
        if ppm > THRESHOLD:
            print("[ALARM] ppm > THRESHOLD: {} ppm!".format(ppm))
    except Exception as e:
        print("Error:", e)
        try:
            mqtt_client = connect_mqtt()
        except:
            pass
    time.sleep(5)
