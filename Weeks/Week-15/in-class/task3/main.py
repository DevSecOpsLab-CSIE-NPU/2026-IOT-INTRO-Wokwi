from machine import Pin, ADC
import time
import network
import ujson
from umqtt.simple import MQTTClient

WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
ACCESS_TOKEN = "OrQ0S820dRe9L8EoR7Wa"
TB_HOST = "thingsboard.cloud"
SEND_INTERVAL = 5
THRESHOLD = 80

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

gas_adc = ADC(Pin(34))
gas_adc.atten(ADC.ATTN_11DB)

print("=== Booting Q3 MQTT ===")
print("[WiFi] Connecting to", WIFI_SSID)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)
timeout = 30
while not wlan.isconnected() and timeout > 0:
    print(".", end="")
    time.sleep_ms(500)
    timeout -= 1
print()

if wlan.isconnected():
    print("[WiFi] Connected:", wlan.ifconfig())
    try:
        mqtt = MQTTClient(client_id=b"wokwi_1114405003", server=TB_HOST, port=1883, user=ACCESS_TOKEN, password=ACCESS_TOKEN)
        mqtt.connect()
        print("[MQTT] Connected to", TB_HOST)
    except Exception as e:
        print("[MQTT] Failed:", e)
        mqtt = None
else:
    print("[WiFi] Failed")
    mqtt = None

last_publish = 0
while True:
    try:
        raw = gas_adc.read()
        ppm = raw_to_ppm(raw)

        if ppm > THRESHOLD:
            print("[ALARM] gas_ppm={} > THRESHOLD={}".format(ppm, THRESHOLD))
        else:
            print("[DEBUG] gas_ppm={} raw={}".format(ppm, raw))

        now = time.ticks_ms()
        if now - last_publish >= SEND_INTERVAL * 1000:
            last_publish = now
            if mqtt:
                telemetry = ujson.dumps({"gas_ppm": ppm})
                mqtt.publish(b"v1/devices/me/telemetry", telemetry)
                print("[MQTT] Published:", telemetry)

    except Exception as e:
        print("[ERROR]", e)

    time.sleep(1)
