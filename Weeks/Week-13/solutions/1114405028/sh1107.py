# sh1107.py 驅動程式
from machine import Pin
import framebuf

class SH1107(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc, rotate=0):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.rotate = rotate
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        for cmd in [
            0xAE, 0xDC, 0x00, 0x81, 0x2F, 0x20, 0x30, 0x40,
            0xA4, 0xA6, 0xAF
        ]: self.write_cmd(cmd)

    def show(self):
        for page in range(self.pages):
            self.write_cmd(0xB0 + page)
            self.write_cmd(0x00)
            self.write_cmd(0x10)
            self.write_data(self.buffer[page * self.width:(page + 1) * self.width])

class SH1107_I2C(SH1107):
    def __init__(self, width, height, i2c, address=0x3C, external_vcc=False, rotate=0):
        self.i2c = i2c
        self.address = address
        self.cmd_buf = bytearray(2)
        super().__init__(width, height, external_vcc, rotate)

    def write_cmd(self, cmd):
        self.cmd_buf[0] = 0x00
        self.cmd_buf[1] = cmd
        self.i2c.writeto(self.address, self.cmd_buf)

    def write_data(self, buf):
        self.i2c.writeto(self.address, b'\x40' + buf)