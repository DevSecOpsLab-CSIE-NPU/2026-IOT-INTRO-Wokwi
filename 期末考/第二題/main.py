from machine import Pin, I2C, ADC
import dht
import framebuf
import time


STUDENT_ID = "1114405040"
DHT22_GPIO = 4
MQ2_GPIO = 32
MQ2_K = 2.54
MQ2_P = 2.467


class SSD1306:
    def __init__(self, width, height, i2c, addr=0x3C):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.pages = height // 8
        self.buffer = bytearray(self.pages * width)
        self.fb = framebuf.FrameBuffer(self.buffer, width, height, framebuf.MONO_VLSB)
        self.init_display()

    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, b"\x80" + bytes([cmd]))

    def write_data(self, data):
        self.i2c.writeto(self.addr, b"\x40" + data)

    def init_display(self):
        for cmd in (
            0xAE, 0x20, 0x00, 0x40, 0xA1, 0xA8, self.height - 1,
            0xC8, 0xD3, 0x00, 0xDA, 0x12, 0xD5, 0x80, 0xD9,
            0xF1, 0xDB, 0x30, 0x81, 0xFF, 0xA4, 0xA6, 0x8D,
            0x14, 0xAF
        ):
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def fill(self, color):
        self.fb.fill(color)

    def text(self, text, x, y, color=1):
        self.fb.text(text, x, y, color)

    def show(self):
        self.write_cmd(0x21)
        self.write_cmd(0)
        self.write_cmd(self.width - 1)
        self.write_cmd(0x22)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)


def raw_to_ppm(raw):
    v = raw / 4095.0
    if v <= 0:
        return 0
    if v >= 1:
        v = 0.999
    ratio = v / (1.0 - v)
    ppm = int(MQ2_K * (ratio ** MQ2_P))
    return int((ppm + 5) // 10) * 10


def show_values(temp, humi, ppm):
    oled.fill(0)
    oled.text("Dacheng AirMon", 0, 0)
    oled.text("Temp:{:>5.1f}C".format(temp), 0, 16)
    oled.text("Humi:{:>5.1f}%".format(humi), 0, 32)
    oled.text("Gas(ppm):{:>4}".format(ppm), 0, 48)
    oled.show()


def show_error(message):
    oled.fill(0)
    oled.text("Dacheng AirMon", 0, 0)
    oled.text("Sensor Error", 0, 24)
    oled.text(message[:16], 0, 40)
    oled.show()


# diagram.json wiring:
# OLED SDA=GPIO21, SCL=GPIO22; DHT22 DATA=GPIO4; MQ2 AO=GPIO32.
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = SSD1306(128, 64, i2c)

dht22 = dht.DHT22(Pin(DHT22_GPIO))
mq2 = ADC(Pin(MQ2_GPIO))
mq2.atten(ADC.ATTN_11DB)

while True:
    try:
        dht22.measure()
        temp = dht22.temperature()
        humi = dht22.humidity()
        raw = mq2.read()
        ppm = raw_to_ppm(raw)

        print("[DEBUG] student={} temp={:.1f}C humi={:.1f}% gas_raw={} gas_ppm={}".format(
            STUDENT_ID, temp, humi, raw, ppm
        ))
        show_values(temp, humi, ppm)
    except Exception as e:
        print("[ERROR]", e)
        show_error(str(e))

    time.sleep(2)
