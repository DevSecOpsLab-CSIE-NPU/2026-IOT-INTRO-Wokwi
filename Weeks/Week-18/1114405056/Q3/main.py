import network
import time
from machine import Pin, ADC, I2C
import ujson
from umqtt.simple import MQTTClient
import ssd1306

# ---------- Configuration (fill these) ----------
WIFI_SSID = 'Wokwi-GUEST'
WIFI_PASS = ''

# ThingsBoard device token (replace with your device's token)
THINGSBOARD_TOKEN = 'YOUR_DEVICE_TOKEN'

# MQTT broker
TB_HOST = 'mqtt.thingsboard.cloud'
TB_PORT = 1883

# MQ2 ADC pin (依學號設定)
MQ2_ADC_PIN = 14

# Upload interval (seconds)
INTERVAL = 5

# Alarm threshold (ppm) — set為你的門檻
# 由使用者提供：50 + 6 * 10 = 110
THRESHOLD = 110

# I2C (optional OLED)
I2C_SCL = 22
I2C_SDA = 21


def connect_wifi(ssid, password, timeout=15):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('[INFO] connecting to WiFi...')
        wlan.connect(ssid, password)
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout:
                raise RuntimeError('WiFi connection timeout')
            time.sleep(0.5)
    print('[INFO] WiFi connected:', wlan.ifconfig())
    return wlan


def read_mq2_ppm(adc):
    raw = adc.read_u16()
    v = raw / 65535 * 3.3
    ppm = int((1 - v / 3.3) * 2000)
    if ppm < 0:
        ppm = 0
    return ppm, raw, v


def main():
    # init OLED (optional)
    try:
        i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
        oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    except Exception:
        oled = None

    # ADC for MQ2
    mq2 = ADC(Pin(MQ2_ADC_PIN))
    try:
        mq2.atten(ADC.ATTN_11DB)
    except Exception:
        pass

    # Connect WiFi
    try:
        connect_wifi(WIFI_SSID, WIFI_PASS)
    except Exception as e:
        print('[ERROR] WiFi failed:', e)

    # Setup MQTT client (ThingsBoard uses device token as username)
    client_id = THINGSBOARD_TOKEN
    try:
        client = MQTTClient(client_id, TB_HOST, port=TB_PORT, user=THINGSBOARD_TOKEN, password='')
        client.connect()
        print('[INFO] MQTT connected to', TB_HOST)
    except Exception as e:
        client = None
        print('[ERROR] MQTT connect failed:', e)

    topic = b'v1/devices/me/telemetry'

    while True:
        try:
            ppm, raw, v = read_mq2_ppm(mq2)
            payload = ujson.dumps({'gas_ppm': ppm})

            # publish to ThingsBoard
            if client:
                try:
                    client.publish(topic, payload, qos=1)
                except Exception as e:
                    print('[WARN] publish failed:', e)

            # update OLED
            if oled:
                try:
                    oled.fill(0)
                    oled.text('Dacheng AirMon', 6, 0)
                    oled.text('Gas: {} ppm'.format(ppm), 0, 20)
                    oled.text('Raw: {}'.format(raw), 0, 36)
                    oled.show()
                except Exception:
                    pass

            # Serial debug
            print('[DEBUG] gas_ppm={} raw={} V={:.2f}'.format(ppm, raw, v))

            # Alarm locally
            if ppm > THRESHOLD:
                print('[ALARM] gas_ppm {} > {}'.format(ppm, THRESHOLD))
            time.sleep(INTERVAL)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print('[ERROR] loop:', e)
            time.sleep(5)


if __name__ == '__main__':
    main()
