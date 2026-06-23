from machine import Pin, ADC
import network
import time
import ujson
from umqtt.simple import MQTTClient

WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
ACCESS_TOKEN = "9uf0heihkm711svtdnvw"
ACCESS_PASSWORD = "g4f5459r96j6tbav1gxi"
TB_HOST = "23.20.176.222"
SEND_INTERVAL = 5
THRESHOLD = 70

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


mq2 = ADC(Pin(35))
mq2.atten(ADC.ATTN_11DB)

print("[WiFi] Connecting to", WIFI_SSID, "...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)

timeout = 30
while not wlan.isconnected() and timeout > 0:
    print(".", end="")
    time.sleep_ms(500)
    timeout -= 1
print()

if not wlan.isconnected():
    print("[WiFi] Failed to connect")
    mqtt_client = None
else:
    print("[WiFi] Connected:", wlan.ifconfig())
    try:
        mqtt_client = MQTTClient(
            client_id=b"p2idddgdbf4048c8x1fs",
            server=TB_HOST,
            port=1883,
            user=ACCESS_TOKEN,
            password=ACCESS_PASSWORD
        )
        mqtt_client.connect()
        print("[MQTT] Connected to", TB_HOST)
    except Exception as exc:
        print("[MQTT] Failed:", exc)
        mqtt_client = None

last_publish_ms = 0

while True:
    try:
        raw = mq2.read()
        ppm = raw_to_ppm(raw)
        print("[DEBUG] gas_raw={}, gas_ppm={}".format(raw, ppm))

        if ppm > THRESHOLD:
            print("[ALARM] gas_ppm={} > THRESHOLD={}".format(ppm, THRESHOLD))

        now = time.ticks_ms()
        if mqtt_client is not None and time.ticks_diff(now, last_publish_ms) >= SEND_INTERVAL * 1000:
            last_publish_ms = now
            alarm = 1 if ppm > THRESHOLD else 0
            payload = ujson.dumps({"gas_ppm": ppm, "alarm": alarm})
            mqtt_client.publish(b"v1/devices/me/telemetry", payload, qos=1)
            print("[MQTT] Published:", payload)

        time.sleep(1)

    except Exception as exc:
        print("[ERROR]", exc)
        time.sleep(2)
