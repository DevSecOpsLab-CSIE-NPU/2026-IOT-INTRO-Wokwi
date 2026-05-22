# sh1107.py - MicroPython SH1107 OLED driver
from micropython import const
import framebuf

# 常數定義
SET_CONTROLS = const(0x00)
SET_DISPLAY_MIN = const(0x10)
SET_MEM_MODE = const(0x20)
SET_PAGE_ADDRESS = const(0xB0)
SET_COL_ADDRESS_MSB = const(0x10)
SET_COL_ADDRESS_LSB = const(0x00)
SET_DISPLAY_START_LINE = const(0xDC)
SET_CONTRAST = const(0x81)
SET_SEG_REMAP = const(0xA0)
SET_MULTIPLEX_RATIO = const(0xA8)
SET_ENTIRE_DISPLAY_ON = const(0xA4)
SET_DISPLAY_NORMAL = const(0xA6)
SET_DISPLAY_OFFSET = const(0xD3)
SET_DC_DC_CONVERTER = const(0xAD)
SET_DISPLAY_OFF = const(0xAE)
SET_DISPLAY_ON = const(0xAF)
SET_SCAN_DIRECTION = const(0xC0)
SET_PRECHARGE_PERIOD = const(0xD5)
SET_VCOM_DESELECT_LEVEL = const(0xDB)

class SH1107(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        self.write_cmd(SET_DISPLAY_OFF)
        self.write_cmd(SET_MEM_MODE)
        self.write_cmd(0x00)  # 頁面定址模式 Page addressing mode
        self.write_cmd(SET_DISPLAY_START_LINE)
        self.write_cmd(0x00)
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(0x80)  # 中等對比度
        self.write_cmd(SET_SEG_REMAP | 0x01)
        self.write_cmd(SET_SCAN_DIRECTION | 0x08)
        self.write_cmd(SET_MULTIPLEX_RATIO)
        self.write_cmd(self.height - 1)
        self.write_cmd(SET_DISPLAY_OFFSET)
        self.write_cmd(0x00)
        self.write_cmd(SET_PRECHARGE_PERIOD)
        self.write_cmd(0x22)
        self.write_cmd(SET_VCOM_DESELECT_LEVEL)
        self.write_cmd(0x35)
        self.write_cmd(SET_DC_DC_CONVERTER)
        self.write_cmd(0x8A)  # 開啟內建 DC-DC 轉換器
        self.write_cmd(SET_ENTIRE_DISPLAY_ON)
        self.write_cmd(SET_DISPLAY_NORMAL)
        self.clear()
        self.show()
        self.write_cmd(SET_DISPLAY_ON)

    def poweroff(self):
        self.write_cmd(SET_DISPLAY_OFF)

    def poweron(self):
        self.write_cmd(SET_DISPLAY_ON)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_DISPLAY_NORMAL | (invert & 1))

    def show(self):
        for page in range(self.pages):
            self.write_cmd(SET_PAGE_ADDRESS | page)
            self.write_cmd(SET_COL_ADDRESS_LSB | 0x00)
            self.write_cmd(SET_COL_ADDRESS_MSB | 0x00)
            self.write_data(self.buffer[page * self.width : (page + 1) * self.width])

    def clear(self):
        fill = b'\x00' * len(self.buffer)
        self.buffer[0:len(self.buffer)] = fill

class SH1107_I2C(SH1107):
    def __init__(self, width, height, i2c, address=0x3C, external_vcc=False, rotate=0):
        self.i2c = i2c
        self.address = address
        self.temp = bytearray(2)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0 (指令控制位元)
        self.temp[1] = cmd
        self.i2c.writeto(self.address, self.temp)

    def write_data(self, buf):
        self.i2c.writeto(self.address, b'\x40' + buf)  # Co=0, D/C#=1 (資料串流)
