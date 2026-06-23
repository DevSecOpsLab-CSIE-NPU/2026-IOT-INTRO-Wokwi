from machine import Pin, ADC
import time
import network
import ujson
from umqtt.simple import MQTTClient

# 學號: 1114405020, 個位數=0, 十位數=2
MQ2_PIN   = 36       # 自訂 AO → GPIO36
THRESHOLD = 50       # 門檻 = 50 + 0×10 = 50 ppm

WIFI_SSID    = "Wokwi-GUEST"
WIFI_PASS    = ""
ACCESS_TOKEN = "nqbxwsrrugs3a77bj4i4"
MQTT_PASS    = "pzcgbajjh274h8jtri07"
TB_HOST      = "thingsboard.cloud"
SEND_INTERVAL = 5

# MQ2 非線性校正公式
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

gas_adc = ADC(Pin(MQ2_PIN))
gas_adc.atten(ADC.ATTN_11DB)

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
    print("[WiFi] Failed to connect!")
    raise SystemExit("WiFi connection failed")

print("[WiFi] Connected, IP:", wlan.ifconfig()[0])

print("[MQTT] Connecting to", TB_HOST, "...")
try:
    mqtt_client = MQTTClient(
        client_id=b"wokwi_03",
        server=TB_HOST,
        port=1883,
        user=ACCESS_TOKEN,
        password=MQTT_PASS
    )
    mqtt_client.connect()
    print("[MQTT] Connected to ThingsBoard Cloud")
except Exception as e:
    print("[MQTT] Failed:", e)
    raise SystemExit("MQTT connection failed")

last_publish = 0

while True:
    try:
        raw = gas_adc.read()
        ppm = raw_to_ppm(raw)

        if ppm > THRESHOLD:
            print("[ALARM]!!! MQ2 偵測到有害氣體濃度超標！目前: {} ppm, 門檻: {} ppm".format(ppm, THRESHOLD))
        else:
            print("[DEBUG] Gas {} ppm".format(ppm))

        now = time.ticks_ms()
        if now - last_publish >= SEND_INTERVAL * 1000:
            last_publish = now
            telemetry = ujson.dumps({"gas_ppm": ppm})
            mqtt_client.publish(b"v1/devices/me/telemetry", telemetry)
            print("[MQTT] Published:", telemetry)

        time.sleep_ms(500)

    except Exception as e:
        print("[ERROR]", e)
        time.sleep(2)
