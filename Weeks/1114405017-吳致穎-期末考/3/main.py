import network
import time
from machine import ADC, Pin
import ubinascii
import ujson
from umqtt.simple import MQTTClient

# --------- CONFIG - fill these before running ---------
WIFI_SSID = 'YOUR_SSID'
WIFI_PASS = 'YOUR_PASSWORD'
# ThingsBoard access token (put your device token here)
TB_TOKEN = 'YOUR_THINGSBOARD_TOKEN'
# ThingsBoard MQTT host
TB_HOST = 'mqtt.thingsboard.cloud'
TB_PORT = 1883

# ADC pin for MQ2 (diagram uses GPIO35)
MQ2_ADC_PIN = 35
# ADC -> ppm mapping max
MQ2_PPM_MAX = 300
# Telemetry upload interval (seconds)
UPLOAD_INTERVAL = 5
# Alarm threshold (ppm) - set to your value or compute from student number
THRESHOLD = 130


def connect_wifi(ssid, password, timeout=15):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
    if not wlan.isconnected():
        print('[INFO] connecting to WiFi', ssid)
        wlan.connect(ssid, password)
        t0 = time.time()
        while not wlan.isconnected():
            if time.time() - t0 > timeout:
                raise RuntimeError('WiFi connection timeout')
            time.sleep(1)
    print('[INFO] WiFi connected, IP:', wlan.ifconfig()[0])
    return wlan.ifconfig()


def mq2_adc_to_ppm(adc_val):
    # linear mapping 0..4095 -> 0..MQ2_PPM_MAX
    return int(adc_val / 4095 * MQ2_PPM_MAX)


def mqtt_connect(token):
    client_id = b'esp32-' + ubinascii.hexlify(machine_unique())
    # use token as username per ThingsBoard MQTT v1
    client = MQTTClient(client_id, TB_HOST, port=TB_PORT, user=token, password='')
    client.connect()
    print('[INFO] MQTT connected to', TB_HOST)
    return client


def machine_unique():
    try:
        import machine
        return machine.unique_id()
    except Exception:
        return b'unknown'


def main():
    # init ADC
    adc = ADC(Pin(MQ2_ADC_PIN))
    try:
        adc.atten(ADC.ATTN_11DB)
    except Exception:
        pass

    # connect WiFi
    try:
        connect_wifi(WIFI_SSID, WIFI_PASS)
    except Exception as e:
        print('[ERROR] WiFi failed:', e)
        return

    # connect MQTT
    try:
        client = mqtt_connect(TB_TOKEN)
    except Exception as e:
        print('[ERROR] MQTT connect failed:', e)
        client = None

    topic = b'v1/devices/me/telemetry'

    while True:
        try:
            a = adc.read()
        except Exception:
            # some ports use read_u16 on other ports
            try:
                a = adc.read_u16()
            except Exception as e:
                print('[ERROR] ADC read failed:', e)
                a = 0

        ppm = mq2_adc_to_ppm(a)
        payload = ujson.dumps({'gas_ppm': ppm})
        print('[DEBUG] ADC={} PPM={}'.format(a, ppm))

        if client is not None:
            try:
                client.publish(topic, payload)
                print('[INFO] published telemetry')
            except Exception as e:
                print('[ERROR] publish failed:', e)
                # try reconnect
                try:
                    client = mqtt_connect(TB_TOKEN)
                except Exception as e2:
                    print('[ERROR] mqtt reconnect failed:', e2)
                    client = None

        # local alarm
        if ppm > THRESHOLD:
            print('[ALARM] gas_ppm {} > THRESHOLD {}'.format(ppm, THRESHOLD))

        time.sleep(UPLOAD_INTERVAL)


if __name__ == '__main__':
    main()
