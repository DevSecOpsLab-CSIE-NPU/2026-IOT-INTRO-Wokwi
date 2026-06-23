from machine import Pin, I2C, ADC
import time
import dht

try:
	import ssd1306
except ImportError:
	# Fallback for this repo layout when running from a Week solution folder.
	import sys

	if "../../../../lib" not in sys.path:
		sys.path.append("../../../../lib")
	import ssd1306


# Fixed OLED I2C pins
I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
OLED_DEFAULT_ADDR = 0x3C

# Pins from diagram.json (student-specific wiring)
DHT22_PIN = 13
MQ2_ADC_PIN = 32
DEBUG_INTERVAL_MS = 2000
MQ2_BASELINE_PPM = 60


def mq2_raw_to_ppm(raw_value: int, baseline_raw: int) -> int:
	"""Linear map using startup baseline: baseline_raw -> MQ2_BASELINE_PPM."""
	if baseline_raw <= 0:
		return 0
	ppm = int((raw_value * MQ2_BASELINE_PPM) / baseline_raw)
	if ppm < 0:
		return 0
	if ppm > 9999:
		return 9999
	return ppm


def pick_oled_addr(i2c):
	devices = i2c.scan()
	print("[DEBUG] I2C scan:", [hex(x) for x in devices])
	if 0x3C in devices:
		return 0x3C
	if 0x3D in devices:
		return 0x3D
	return OLED_DEFAULT_ADDR


def draw_screen(oled, temp_c, humi, gas_ppm):
	oled.fill(0)
	oled.text("Dacheng AirMon", 0, 0)
	oled.text("Temp: {:.1f} C".format(temp_c), 0, 16)
	oled.text("Humi: {:.1f} %".format(humi), 0, 32)
	oled.text("Gas : {} ppm".format(gas_ppm), 0, 48)
	oled.show()


def main():
	i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))
	oled_addr = pick_oled_addr(i2c)
	print("[DEBUG] OLED addr =", hex(oled_addr))
	oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=oled_addr)
	oled.contrast(255)

	# Power-on self test: if this text is visible, OLED init/path is OK.
	oled.fill(0)
	oled.text("OLED READY", 0, 0)
	oled.text("Addr: {}".format(hex(oled_addr)), 0, 16)
	oled.show()
	time.sleep(1)

	dht22 = dht.DHT22(Pin(DHT22_PIN))
	mq2 = ADC(Pin(MQ2_ADC_PIN))
	mq2.atten(ADC.ATTN_11DB)  # Full-scale range for ESP32 ADC
	baseline_raw = max(1, mq2.read())
	print("[DEBUG] MQ2 baseline_raw={} -> {}ppm".format(baseline_raw, MQ2_BASELINE_PPM))
	loop_count = 0

	while True:
		start_ms = time.ticks_ms()
		loop_count += 1
		try:
			dht22.measure()
			temp_c = dht22.temperature()
			humi = dht22.humidity()
		except Exception as err:
			print("[DEBUG] DHT22 read failed:", err)
			temp_c = 0.0
			humi = 0.0

		mq2_raw = mq2.read()
		gas_ppm = mq2_raw_to_ppm(mq2_raw, baseline_raw)

		draw_screen(oled, temp_c, humi, gas_ppm)

		print(
			"[DEBUG #{:03d}] OLED={} Temp={:.1f}C Humi={:.1f}% MQ2_RAW={} BaseRaw={} Gas={}ppm".format(
				loop_count,
				hex(oled_addr),
				temp_c,
				humi,
				mq2_raw,
				baseline_raw,
				gas_ppm,
			)
		)

		elapsed = time.ticks_diff(time.ticks_ms(), start_ms)
		wait_ms = DEBUG_INTERVAL_MS - elapsed
		if wait_ms > 0:
			time.sleep_ms(wait_ms)


main()
