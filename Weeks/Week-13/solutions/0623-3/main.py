from machine import Pin, ADC, reset
import network
import time
import ujson

try:
	from umqtt.simple import MQTTClient
except ImportError:
	print("[ERROR] umqtt.simple not found; using fallback stub")
	class MQTTClient:
		def __init__(self, *args, **kwargs):
			pass
		def connect(self):
			pass
		def publish(self, *args, **kwargs):
			pass
		def disconnect(self):
			pass


# ==================== Configuration ====================
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

# ThingsBoard MQTT details
MQTT_BROKER = "mqtt.thingsboard.cloud"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "ax1xd7hbasvmgq6ktxm1"
MQTT_USERNAME = "a6pj4yyjon8qttm410pg"
MQTT_PASSWORD = "higmnv97j222gnojz1bi"

# MQ2 Sensor
MQ2_ADC_PIN = 32

# Alarm Threshold (学号对应，题目给定)
THRESHOLD_PPM = 60  # PPM超过60触发警报

# Console output interval (seconds)
CONSOLE_INTERVAL = 2

# Telemetry upload interval (seconds)
TELEMETRY_INTERVAL = 5


# ==================== Helper Functions ====================
def mq2_raw_to_ppm(raw_value: int, baseline_raw: int) -> int:
	"""Map raw value relative to startup baseline so baseline is around 60ppm."""
	if baseline_raw <= 0:
		return 0
	ppm = int((raw_value * THRESHOLD_PPM) / baseline_raw)
	return max(0, min(9999, ppm))


def connect_wifi():
	"""Connect to WiFi network."""
	print("[INFO] Connecting to WiFi: {}...".format(WIFI_SSID))
	wlan = network.WLAN(network.STA_IF)
	wlan.active(True)
	wlan.connect(WIFI_SSID, WIFI_PASS)
	
	timeout = 20
	while timeout > 0:
		if wlan.isconnected():
			print("[INFO] WiFi connected! IP:", wlan.ifconfig()[0])
			return wlan
		timeout -= 1
		time.sleep(0.5)
	
	print("[ERROR] WiFi connection failed after 10 seconds")
	return None


def connect_mqtt():
	"""Connect to ThingsBoard MQTT broker."""
	print("[INFO] Connecting to MQTT: {}:{}...".format(MQTT_BROKER, MQTT_PORT))
	try:
		client = MQTTClient(
			client_id=MQTT_CLIENT_ID,
			server=MQTT_BROKER,
			port=MQTT_PORT,
			user=MQTT_USERNAME,
			password=MQTT_PASSWORD
		)
		client.connect()
		print("[INFO] MQTT connected!")
		return client
	except Exception as err:
		print("[ERROR] MQTT connection failed:", err)
		return None


def publish_telemetry(client, gas_ppm):
	"""Publish gas_ppm telemetry to ThingsBoard."""
	if client is None:
		return False
	
	payload = ujson.dumps({"gas_ppm": gas_ppm})
	topic = "v1/devices/me/telemetry"
	
	try:
		client.publish(topic, payload, qos=1)
		print("[MQTT] Published: {} -> {}".format(topic, payload))
		return True
	except Exception as err:
		print("[ERROR] MQTT publish failed:", err)
		return False


# ==================== Main Program ====================
def main():
	print("[START] ThingsBoard MQ2 Telemetry")
	
	# Connect WiFi
	wlan = connect_wifi()
	if wlan is None:
		print("[ERROR] Cannot proceed without WiFi")
		return
	
	# Connect MQTT
	mqtt_client = connect_mqtt()
	if mqtt_client is None:
		print("[WARN] MQTT connection failed; will continue in offline mode")
	
	# Initialize MQ2
	mq2 = ADC(Pin(MQ2_ADC_PIN))
	mq2.atten(ADC.ATTN_11DB)

	# Capture startup baseline (average of 10 samples)
	baseline_sum = 0
	for _ in range(10):
		baseline_sum += mq2.read()
		time.sleep(0.05)
	baseline_raw = baseline_sum // 10
	
	print("[INFO] Alarm threshold: {}ppm".format(THRESHOLD_PPM))
	print("[INFO] Baseline MQ2_RAW={} (mapped near {}ppm)".format(baseline_raw, THRESHOLD_PPM))
	
	loop_count = 0
	last_console_ms = time.ticks_ms()
	last_publish_ms = time.ticks_ms()
	
	while True:
		current_ms = time.ticks_ms()
		
		# Read MQ2 (every iteration)
		mq2_raw = mq2.read()
		gas_ppm = mq2_raw_to_ppm(mq2_raw, baseline_raw)
		
		# Console output every CONSOLE_INTERVAL seconds
		console_elapsed_ms = time.ticks_diff(current_ms, last_console_ms)
		if console_elapsed_ms >= CONSOLE_INTERVAL * 1000:
			loop_count += 1
			
			# Print PPM and alarm status
			if gas_ppm > THRESHOLD_PPM:
				print("[ALARM #{:03d}] *** GAS_PPM={} MQ2_RAW={} EXCEEDS THRESHOLD={} ***".format(
					loop_count, gas_ppm, mq2_raw, THRESHOLD_PPM
				))
			else:
				print("[OK #{:03d}] GAS_PPM={} MQ2_RAW={}".format(
					loop_count, gas_ppm, mq2_raw
				))
			
			last_console_ms = current_ms
		
		# Publish telemetry every TELEMETRY_INTERVAL seconds
		publish_elapsed_ms = time.ticks_diff(current_ms, last_publish_ms)
		if publish_elapsed_ms >= TELEMETRY_INTERVAL * 1000:
			print("[MQTT] Sending gas_ppm={}".format(gas_ppm))
			if mqtt_client is not None:
				publish_telemetry(mqtt_client, gas_ppm)
			last_publish_ms = current_ms
		
		# Small delay to avoid busy loop
		time.sleep(0.1)


if __name__ == "__main__":
	main()
