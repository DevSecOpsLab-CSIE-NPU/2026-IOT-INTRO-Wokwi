from machine import Pin, I2C
import ssd1306
try:
    from machine import SoftI2C
except Exception:
    SoftI2C = None
import framebuf

# 嘗試自動偵測 I2C bus 與 OLED 地址
def find_oled(bus_candidates=(0, 1), scl_pin=22, sda_pin=21, addr_candidates=(0x3C, 0x3D)):
    # 嘗試多次掃描以等待模擬器或 OLED 啟動
    import time
    for bus in bus_candidates:
        devices = []
        for attempt in range(4):
            try:
                i2c = I2C(bus, scl=Pin(scl_pin), sda=Pin(sda_pin))
                devices = i2c.scan()
            except Exception:
                devices = []
            if devices:
                break
            time.sleep(0.08)
        if devices:
            for a in addr_candidates:
                if a in devices:
                    print('Found OLED on bus', bus, 'addr', hex(a))
                    return i2c, a
            # 若找不到預設地址，回傳第一個偵測到的裝置地址
            print('I2C devices on bus', bus, ':', devices)
            return i2c, devices[0]
    # 嘗試軟體 I2C
    if SoftI2C is not None:
        try:
            si2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
            sdev = si2c.scan()
            if sdev:
                for a in addr_candidates:
                    if a in sdev:
                        print('Found OLED on SoftI2C addr', hex(a))
                        return si2c, a
                print('I2C devices on SoftI2C:', sdev)
                return si2c, sdev[0]
        except Exception:
            pass
    print('No I2C devices found on buses', bus_candidates)
    return None, None


oled_width = 128
oled_height = 64
i2c, detected_addr = find_oled()
if i2c is None:
    raise RuntimeError('OLED not found; 檢查 wiring/diagram.json 與 I2C 腳位設定')
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c, addr=detected_addr)

FONT_3X5 = {
    "A": ("111", "101", "111", "101", "101"),
    "C": ("111", "100", "100", "100", "111"),
    "D": ("110", "101", "101", "101", "110"),
    "E": ("111", "100", "110", "100", "111"),
    "F": ("111", "100", "110", "100", "100"),
    "G": ("111", "100", "101", "101", "111"),
    "H": ("101", "101", "111", "101", "101"),
    "I": ("111", "010", "010", "010", "111"),
    "L": ("100", "100", "100", "100", "111"),
    "N": ("101", "111", "111", "111", "101"),
    "O": ("111", "101", "101", "101", "111"),
    "P": ("111", "101", "111", "100", "100"),
    "R": ("111", "101", "111", "110", "101"),
    "S": ("111", "100", "111", "001", "111"),
    "T": ("111", "010", "010", "010", "010"),
    "U": ("101", "101", "101", "101", "111"),
    "V": ("101", "101", "101", "101", "010"),
    "Y": ("101", "101", "010", "010", "010"),
    "0": ("111", "101", "101", "101", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "6": ("111", "100", "111", "101", "111"),
    " ": ("000", "000", "000", "000", "000"),
    "?": ("111", "001", "011", "000", "010"),
}


def draw_tiny_text(display, text, x, y, color=1):
    cursor_x = x
    for ch in text.upper():
        glyph = FONT_3X5.get(ch, FONT_3X5["?"])
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    display.pixel(cursor_x + col, y + row, color)
        cursor_x += 4

def draw_circle(display, cx, cy, r, color=1):
    x = r
    y = 0
    err = 0
    while x >= y:
        display.pixel(cx + x, cy + y, color)
        display.pixel(cx + y, cy + x, color)
        display.pixel(cx - y, cy + x, color)
        display.pixel(cx - x, cy + y, color)
        display.pixel(cx - x, cy - y, color)
        display.pixel(cx - y, cy - x, color)
        display.pixel(cx + y, cy - x, color)
        display.pixel(cx + x, cy - y, color)
        y += 1
        if err <= 0:
            err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1


def draw_star(display, cx, cy, size, color=1):
    # Simple 5-point star for 128x64 OLED
    pts = [
        (cx, cy - size),
        (cx + int(size * 0.35), cy - int(size * 0.25)),
        (cx + size, cy - int(size * 0.2)),
        (cx + int(size * 0.5), cy + int(size * 0.25)),
        (cx + int(size * 0.6), cy + size),
        (cx, cy + int(size * 0.45)),
        (cx - int(size * 0.6), cy + size),
        (cx - int(size * 0.5), cy + int(size * 0.25)),
        (cx - size, cy - int(size * 0.2)),
        (cx - int(size * 0.35), cy - int(size * 0.25)),
    ]
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        display.line(x1, y1, x2, y2, color)


oled.fill(0)
draw_circle(oled, 64, 32, 28, 1)
draw_star(oled, 64, 32, 9, 1)
draw_tiny_text(oled, "Penghu", 2, 2)
draw_tiny_text(oled, "University", 2, 10)

draw_tiny_text(oled, "Dept", 2, 24)
draw_tiny_text(oled, "of", 12, 32)
draw_tiny_text(oled, "CSIE", 2, 40)


draw_tiny_text(oled, "of Science", 2, 52)
draw_tiny_text(oled, "and Technology", 2, 58)

oled.text("2026", 96, 2)

# === 自動產生的中文點陣資料 ===
# 字型: NotoSerifCJK-Bold.ttc
# 大小: 32x32
# '花'  32x32
FONT_82B1 = bytearray(
    b'\x00\x00\x00\x00\x00\x7c\x1e\x00\x00\x78\x1c\x10'
    b'\x00\x78\x1c\x18\x00\x78\x1c\x3c\x7f\xff\xff\xfe'
    b'\x00\x78\x1c\x00\x00\x78\x1c\x00\x00\x78\x1c\x00'
    b'\x00\x00\x00\x00\x00\xf0\xf8\x00\x00\xf8\xf0\x00'
    b'\x01\xf0\xf0\x70\x01\xe0\xf0\xf8\x03\xc0\xf1\xf0'
    b'\x03\xc0\xf1\xe0\x07\xe0\xf3\xc0\x0f\xe0\xf7\x00'
    b'\x0d\xe0\xfc\x00\x19\xe0\xf0\x00\x31\xe0\xf0\x00'
    b'\x41\xe0\xf0\x00\x01\xe0\xf0\x04\x01\xe0\xf0\x04'
    b'\x01\xe0\xf0\x04\x01\xe0\xf0\x0c\x01\xe0\xf0\x0c'
    b'\x01\xe0\xff\xfe\x01\xe0\xff\xfe\x01\xe0\x7f\xfe'
    b'\x01\xc0\x0f\xe0\x00\x00\x00\x00'
)

# '火'  32x32
FONT_706B = bytearray(
    b'\x00\x00\x00\x00\x00\x07\x00\x00\x00\x07\x80\x00'
    b'\x00\x07\x80\x00\x00\x07\x80\x00\x00\x07\x80\x00'
    b'\x00\x07\x80\x00\x01\x07\x80\x60\x01\x07\x80\xf0'
    b'\x01\x87\xc0\xfc\x01\x87\xc1\xf0\x03\x87\xc3\xe0'
    b'\x03\x87\xc3\xc0\x07\x8f\x47\x00\x0f\x8f\x6e\x00'
    b'\x1f\x0f\x68\x00\x1f\x0f\x30\x00\x1e\x0f\x30\x00'
    b'\x00\x1e\x30\x00\x00\x1e\x38\x00\x00\x1e\x1c\x00'
    b'\x00\x3c\x1e\x00\x00\x38\x1e\x00\x00\x78\x0f\x80'
    b'\x00\xf0\x0f\xc0\x01\xe0\x07\xf0\x03\xc0\x03\xfc'
    b'\x07\x00\x01\xfe\x0e\x00\x00\xf8\x18\x00\x00\x70'
    b'\x40\x00\x00\x10\x00\x00\x00\x00'
)

# '節'  32x32
FONT_7BC0 = bytearray(
    b'\x07\x80\x38\x00\x07\x84\x7c\x18\x07\x0e\x78\x3c'
    b'\x0f\xff\x7f\xfe\x0e\xe0\xe7\x00\x1c\x70\xc3\x80'
    b'\x18\x71\x83\xc0\x30\x71\x03\xc0\x60\x74\x01\x90'
    b'\x0c\x0e\x38\x38\x0f\xff\x3f\xfc\x0e\x0f\x38\x3c'
    b'\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c\x0f\xff\x38\x3c'
    b'\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c\x0e\x0f\x38\x3c'
    b'\x0e\x0f\x38\x3c\x0f\xff\x38\x3c\x0e\x0e\x38\x3c'
    b'\x0e\x20\x38\x3c\x0e\x38\x38\x3c\x0e\x1c\x38\xf8'
    b'\x0e\x1e\x38\x78\x1f\xff\x38\x78\x7f\xc7\x38\x60'
    b'\x7f\x07\x38\x00\x3c\x07\x38\x00\x20\x00\x38\x00'
    b'\x00\x00\x30\x00\x00\x00\x00\x00'
)

# 字 → bytearray 對照表
CHARS = {
    '花': (FONT_82B1, 32, 32),
    '火': (FONT_706B, 32, 32),
    '節': (FONT_7BC0, 32, 32),
}

def draw_char(oled, char, x, y, shrink=1):
    """在 OLED 指定位置畫一個中文字，可用 shrink 縮小顯示"""
    if char not in CHARS:
        return
    data, w, h = CHARS[char]
    fb = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
    if shrink <= 1:
        oled.blit(fb, x, y)
        return

    # 以取樣方式縮小字型，例如 32x32 搭配 shrink=2 會輸出 16x16。
    out_w = (w + shrink - 1) // shrink
    out_h = (h + shrink - 1) // shrink
    for oy in range(out_h):
        sy = oy * shrink
        for ox in range(out_w):
            sx = ox * shrink
            if fb.pixel(sx, sy):
                oled.pixel(x + ox, y + oy, 1)

def draw_text(oled, text, x, y, spacing=0, shrink=1):
    """在 OLED 畫一串中文字，可用 shrink 縮小顯示"""
    cx = x
    for ch in text:
        if ch in CHARS:
            _, w, _ = CHARS[ch]
            draw_char(oled, ch, cx, y, shrink=shrink)
            draw_w = (w + shrink - 1) // shrink
            cx += draw_w + spacing


def draw_text_vertical(oled, text, x, y, spacing=0, shrink=1):
    """在 OLED 直排文字（由上到下）"""
    cy = y
    for ch in text:
        if ch in CHARS:
            _, _, h = CHARS[ch]
            draw_char(oled, ch, x, cy, shrink=shrink)
            draw_h = (h + shrink - 1) // shrink
            cy += draw_h + spacing


draw_text_vertical(oled, "花火節", 100, 12, spacing=1, shrink=2)


oled.show()


# --- 以下為動畫效果: 簡單煙火與閃爍、滾動文字 ---
import time


def _xorshift32(seed=[int(time.ticks_ms() & 0xFFFFFFFF)]):
    # closure 隨機產生器（簡單 xorshift32）
    while True:
        x = seed[0]
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17) & 0xFFFFFFFF
        x ^= (x << 5) & 0xFFFFFFFF
        seed[0] = x
        yield x & 0x7FFFFFFF


rand_gen = _xorshift32()


def randrange(a, b):
    return a + (next(rand_gen) % (b - a + 1))


def sparkle(oled, count=20):
    pts = []
    for _ in range(count):
        x = randrange(0, oled_width - 1)
        y = randrange(0, oled_height - 1)
        pts.append((x, y))
        oled.pixel(x, y, 1)
    oled.show()
    time.sleep(0.06)
    for x, y in pts:
        oled.pixel(x, y, 0)


def fireworks(oled, cx, cy, max_r=20):
    # 簡單擴散圓環與星形
    for r in range(2, max_r, 3):
        draw_circle(oled, cx, cy, r, 1)
        draw_star(oled, cx, cy, max(4, r // 3), 1)
        oled.show()
        time.sleep(0.08)
        draw_circle(oled, cx, cy, r, 0)
        draw_star(oled, cx, cy, max(4, r // 3), 0)


def marquee(oled, text, y, speed=0.08):
    w = oled_width
    text_w = len(text) * 8
    for offset in range(w, -text_w - 1, -1):
        oled.fill_rect(0, y, w, 10, 0)
        oled.text(text, offset, y)
        oled.show()
        time.sleep(speed)


try:
    while True:
        # 背景: 保留左上 logo 與中文直排
        oled.fill(0)
        draw_text_vertical(oled, "花火節", 100, 12, spacing=1, shrink=2)
        draw_circle(oled, 64, 18, 14, 1)
        draw_star(oled, 64, 18, 6, 1)
        oled.text("2026", 96, 2)

        # 閃爍星星
        for _ in range(6):
            sparkle(oled, count=14)

        # 主要煙火（隨機位置）
        for _ in range(3):
            fx = randrange(20, oled_width - 20)
            fy = randrange(8, oled_height - 20)
            fireworks(oled, fx, fy, max_r=18)

        # 滾動底部文字
        marquee(oled, "  Penghu Fireworks 2026 ", 52, speed=0.02)

except Exception:
    # 若有錯誤，簡單顯示靜態畫面
    oled.fill(0)
    oled.text("Error", 48, 28)
    oled.show()


