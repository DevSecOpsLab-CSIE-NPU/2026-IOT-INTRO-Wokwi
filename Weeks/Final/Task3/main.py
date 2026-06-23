from machine import ADC, Pin
import network
import time
import ujson
from umqtt.simple import MQTTClient

print("Task3 MQTT test started")

SSID = "Wokwi-GUEST"
PASSWORD = ""

SERVER = "mqtt.thingsboard.cloud"
PORT = 1883
TOPIC = "v1/devices/me/telemetry"

ACCESS_TOKEN = "nq7jggnsryfmkuaqhzr"
MQTT_PASSWORD = "ie2tu1h7scalwl9yd187"
CLIENT_ID = "esp32-mq2-1114405013"

MQ2_PIN = 35
THRESHOLD = 80

mq2_adc = ADC(Pin(MQ2_PIN))
mq2_adc.atten(ADC.ATTN_11DB)


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print("Connecting WiFi...")
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)

    print()
    print("WiFi connected")
    print("IP config:", wlan.ifconfig())


def connect_mqtt():
    print("Connecting MQTT...")

    client = MQTTClient(
        CLIENT_ID,
        SERVER,
        port=PORT,
        user=ACCESS_TOKEN,
        password=MQTT_PASSWORD,
        keepalive=60
    )

    client.connect()
    print("MQTT connected")
    return client


connect_wifi()
client = connect_mqtt()

while True:
    raw = mq2_adc.read()
    gas_ppm = int(raw * 1000 / 4095)

    payload = ujson.dumps({
        "gas_ppm": gas_ppm
    })

    client.publish(TOPIC, payload, qos=1)

    print("[TELEMETRY] gas_ppm={}".format(gas_ppm))

    if gas_ppm > THRESHOLD:
        print("[ALARM] gas_ppm={} over threshold={}".format(gas_ppm, THRESHOLD))

    time.sleep(5)