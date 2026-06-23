from machine import Pin, I2C, ADC
import time
import dht
import ssd1306
import sys
import select


STUDENT_ID = "1114405029"
DHT_PIN = 33
MQ2_PIN = 34
OLED_SCL = 22
OLED_SDA = 21
threshold = 140
OLED_UPDATE_MS = 2000


def raw_to_ppm(raw):
    return int((raw / 4095) * 300)


def update_oled(oled, temp, humi, ppm):
    oled.fill(0)
    oled.text("Dacheng AirMon", 0, 0)
    oled.text("Temp: {:.1f} C".format(temp), 0, 16)
    oled.text("Humi: {:.1f} %".format(humi), 0, 32)
    oled.text("Gas : {:3d} ppm".format(ppm), 0, 48)
    oled.show()


def print_help():
    print("Commands:")
    print("  help or ?        show this help")
    print("  status          print latest sensor values")
    print("  threshold <ppm> set alarm threshold")
    print("  id              print student ID")


def print_status(temp, humi, raw, ppm):
    status = "ALARM" if ppm >= threshold else "OK"
    print("[STATUS] id={} temp={:.1f}C humi={:.1f}% raw={} gas={}ppm threshold={} status={}".format(
        STUDENT_ID, temp, humi, raw, ppm, threshold, status
    ))


def handle_command(line, temp, humi, raw, ppm):
    global threshold

    parts = line.strip().split()
    if not parts:
        return

    cmd = parts[0].lower()
    if cmd in ("help", "?"):
        print_help()
    elif cmd == "status":
        print_status(temp, humi, raw, ppm)
    elif cmd == "id":
        print("[ID]", STUDENT_ID)
    elif cmd == "threshold":
        if len(parts) != 2:
            print("[ERROR] Usage: threshold <ppm>")
            return
        try:
            value = int(parts[1])
            if value < 0:
                raise ValueError
            threshold = value
            print("[OK] threshold={} ppm".format(threshold))
        except ValueError:
            print("[ERROR] threshold must be a non-negative integer")
    else:
        print("[ERROR] Unknown command: {}".format(line))
        print("Type 'help' for commands.")


i2c = I2C(0, scl=Pin(OLED_SCL), sda=Pin(OLED_SDA))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

dht22 = dht.DHT22(Pin(DHT_PIN))
mq2 = ADC(Pin(34))
mq2.atten(ADC.ATTN_11DB)

stdin_poll = select.poll()
stdin_poll.register(sys.stdin, select.POLLIN)

last_oled_update = time.ticks_ms() - OLED_UPDATE_MS
last_temp = 0.0
last_humi = 0.0
last_raw = 0
last_ppm = 0

print("Q2 OLED sensor monitor ready. Type 'help' for commands.")

while True:
    now = time.ticks_ms()

    if stdin_poll.poll(0):
        handle_command(sys.stdin.readline(), last_temp, last_humi, last_raw, last_ppm)

    if time.ticks_diff(now, last_oled_update) >= OLED_UPDATE_MS:
        last_oled_update = now

        try:
            dht22.measure()
            last_temp = dht22.temperature()
            last_humi = dht22.humidity()
        except Exception as exc:
            print("[DHT22] Read failed:", exc)

        last_raw = mq2.read()
        last_ppm = raw_to_ppm(last_raw)

        update_oled(oled, last_temp, last_humi, last_ppm)
        print("[DEBUG] Temp: {:.1f} C, Humi: {:.1f} %, raw: {}, gas_ppm: {} ppm, threshold: {}".format(
            last_temp, last_humi, last_raw, last_ppm, threshold
        ))

    time.sleep_ms(100)
