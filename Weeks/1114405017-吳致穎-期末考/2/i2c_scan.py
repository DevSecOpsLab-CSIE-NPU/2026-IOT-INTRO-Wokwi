from machine import Pin, I2C
import time

SCL = 22
SDA = 21

print('Starting I2C scan on SCL={}, SDA={}'.format(SCL, SDA))
try:
    i2c = I2C(0, scl=Pin(SCL), sda=Pin(SDA))
    time.sleep(0.1)
    devices = i2c.scan()
    if devices:
        print('I2C devices found:')
        for d in devices:
            print(' - 0x{:02x}'.format(d))
    else:
        print('No I2C devices found')
except Exception as e:
    print('I2C scan failed:', e)
