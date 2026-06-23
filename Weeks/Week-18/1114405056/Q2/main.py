from machine import Pin, I2C, ADC
import ssd1306
import dht
import time

# --- 可調整參數（請依學號設定）
# DHT 與 MQ2 腳位請務必與 diagram.json 一致
DHT_PIN = 25      # 改為學號指定 GPIO25
MQ2_ADC_PIN = 14  # 改為學號指定 GPIO14 (AOUT)

# I2C 固定腳位
I2C_SCL = 22
I2C_SDA = 21


def read_mq2_ppm(adc):
    # 簡單示範換算：以 ADC 電壓和比例回推一個相對 ppm 值（示範用途）
    raw = adc.read_u16()  # 0..65535
    v = raw / 65535 * 3.3
    # 轉成相對濃度示範 (越高電壓代表越低濃度) -> ppm 越低
    ppm = int((1 - v / 3.3) * 2000)
    if ppm < 0:
        ppm = 0
    return ppm, raw, v


def main():
    # I2C + OLED
    # 嘗試 I2C bus 0，若沒裝置再嘗試 bus 1
    devices = []
    for bus in (0, 1):
        try:
            i2c = I2C(bus, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
            devices = i2c.scan()
        except Exception:
            devices = []
        print('[DEBUG] I2C bus', bus, 'devices:', devices)
        if devices:
            break

    addr = 0x3C
    if 0x3C not in devices and 0x3D in devices:
        addr = 0x3D
    oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=addr)

    # DHT22
    d = dht.DHT22(Pin(DHT_PIN))

    # MQ2 (ADC)
    mq2 = ADC(Pin(MQ2_ADC_PIN))
    try:
        mq2.atten(ADC.ATTN_11DB)
    except Exception:
        pass

    oled.fill(0)
    oled.text('Dacheng AirMon', 8, 0)
    oled.show()

    while True:
        try:
            d.measure()
            t = d.temperature()
            h = d.humidity()
        except Exception as e:
            t = None
            h = None

        try:
            ppm, raw, v = read_mq2_ppm(mq2)
        except Exception as e:
            ppm = None
            raw = 0
            v = 0

        # 顯示到 OLED
        oled.fill(0)
        oled.text('Dacheng AirMon', 8, 0)
        if t is not None:
            oled.text('T:{:.1f}C'.format(t), 0, 16)
        else:
            oled.text('T: ---', 0, 16)
        if h is not None:
            oled.text('H:{:.1f}%'.format(h), 0, 32)
        else:
            oled.text('H: ---', 0, 32)
        if ppm is not None:
            oled.text('Gas:{}ppm'.format(ppm), 0, 48)
        else:
            oled.text('Gas: ---', 0, 48)
        oled.show()

        # Serial debug
        print('[DEBUG] T={}C H={}%) Raw={} V={:.2f} PPM={}'.format(
            t if t is not None else 'err',
            h if h is not None else 'err',
            raw, v, ppm if ppm is not None else 'err'
        ))

        time.sleep(2)


if __name__ == '__main__':
    main()
