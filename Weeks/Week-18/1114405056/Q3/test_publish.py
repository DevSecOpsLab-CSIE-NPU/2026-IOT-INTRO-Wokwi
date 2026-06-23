import json
import time
import sys
from paho.mqtt import client as mqtt

THINGSBOARD_HOST = 'mqtt.thingsboard.cloud'
THINGSBOARD_PORT = 1883
THINGSBOARD_TOKEN = 'mDNozBCEP2EDkDm2FfcB'

topic = 'v1/devices/me/telemetry'
payload = json.dumps({'gas_ppm': 150})

client = mqtt.Client()
client.username_pw_set(THINGSBOARD_TOKEN)

try:
    client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)
except Exception as e:
    print('CONNECT_ERROR', e)
    sys.exit(2)

rc = client.publish(topic, payload, qos=1)
rc.wait_for_publish()
print('PUBLISHED', payload, 'rc:', rc.rc)
client.disconnect()
