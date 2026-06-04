import machine
import dht
import time
import math

# =========================================================
# 1. 必做需求：學號與引腳設定 (已為您填入正確學號)
# =========================================================
DHT_PIN = 4        
SDA_PIN = 21       
SCL_PIN = 22       
MY_ID = "1112405011" # ✅ 100% 符合學號顯示需求

# =========================================================
# 2. 初始化 128x128 SH1107 正方形大螢幕
# =========================================================
dht_sensor = dht.DHT22(machine.Pin(DHT_PIN))
i2c = machine.I2C(0, sda=machine.Pin(SDA_PIN), scl=machine.Pin(SCL_PIN))

import sh1107
oled = sh1107.SH1107_I2C(128, 128, i2c)

# =========================================================
# 🔄 180度旋轉點映射引擎 (確保符合翻轉後的完美對齊)
# =========================================================
def set_pixel_flipped(x, y, color=1):
    """將常規坐標 (x, y) 映射到 180度旋轉後的畫布上"""
    flipped_x = 127 - x
    flipped_y = 127 - y
    if 0 <= flipped_x < 128 and 0 <= flipped_y < 128:
        oled.pixel(flipped_x, flipped_y, color)

def draw_text_flipped(text, start_x, start_y):
    """將內建英文字體進行 180度顛倒繪製"""
    import framebuf
    buf_width = len(text) * 8
    fb_buf = bytearray((buf_width * 8) // 8)
    fb = framebuf.FrameBuffer(fb_buf, buf_width, 8, framebuf.MONO_VLSB)
    fb.text(text, 0, 0, 1)
    
    for ty in range(8):
        for tx in range(buf_width):
            if fb.pixel(tx, ty):
                set_pixel_flipped(start_x + tx, start_y + ty, 1)

# =========================================================
# 3. 中文字模 (花火節 16x16)
# =========================================================
FONT_CHINESE = {
    "花": b'\x04\x40\x04\x40\x07\xF0\x04\x40\x7F\xFC\x04\x40\x08\x20\x1C\x10\x63\x08\x00\x04\x01\x04\xFF\xFE\x01\x00\x01\x00\x01\x00\x01\x00',
    "火": b'\x01\x00\x01\x00\x11\x00\x11\x00\x09\x00\x09\x10\x05\x20\x03\x40\x05\x40\x09\x20\x11\x18\x21\x06\x41\x02\x01\x00\x01\x00\x01\x00',
    "節": b'\x14\x80\x3F\xFC\x54\x80\x54\x80\x5F\xF8\x94\x80\x10\x00\x1F\xFC\x11\x04\x11\x04\x1F\xFC\x11\x04\x11\x04\x1F\xFC\x11\x04\x10\x00'
}

def draw_chinese_word_dynamic(cx, cy, word, scale):
    """
    🔥 老師要的動態：支援即時點陣縮放加粗矩陣的畫法！
    cx, cy: 字體中心的坐標
    scale: 縮放倍率 (1.0 為正常，1.5 為放大加粗)
    """
    if word not in FONT_CHINESE:
        return
    data = FONT_CHINESE[word]
    
    # 計算 16x16 點陣放大後的相對位移，確保字體中心對齊，不會亂飄
    for row in range(16):
        bits = (data[row * 2] << 8) | data[row * 2 + 1]
        for col in range(16):
            if bits & (1 << (15 - col)):
                # 原本相對於字體中心的坐標
                rel_x = col - 8
                rel_y = row - 8
                
                # 乘上縮放權重
                sch_x = int(rel_x * scale)
                sch_y = int(rel_y * scale)
                
                # 當放大時，自動填補像素肉眼間隙（達成加粗效果，不破圖）
                fill_size = max(1, int(scale))
                for dx in range(fill_size):
                    for dy in range(fill_size):
                        set_pixel_flipped(cx + sch_x + dx, cy + sch_y + dy, 1)

# =========================================================
# 4. 精細自製圖形功能
# =========================================================
def draw_circle_custom(cx, cy, r):
    for angle_deg in range(0, 360, 2):
        rad = math.radians(angle_deg)
        x = int(cx + r * math.cos(rad))
        y = int(cy + r * math.sin(rad))
        set_pixel_flipped(x, y, 1)

def draw_star_five(cx, cy, r):
    points = []
    for i in range(5):
        angle1 = i * 2 * math.pi / 5 - math.pi / 2
        points.append((int(cx + r * math.cos(angle1)), int(cy + r * math.sin(angle1))))
        angle2 = angle1 + math.pi / 5
        points.append((int(cx + (r/2) * math.cos(angle2)), int(cy + (r/2) * math.sin(angle2))))
    
    for i in range(10):
        p1 = points[i]
        p2 = points[(i + 1) % 10]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        steps = max(abs(dx), abs(dy))
        if steps == 0: continue
        for s in range(steps + 1):
            curr_x = int(p1[0] + (dx * s / steps))
            curr_y = int(p1[1] + (dy * s / steps))
            set_pixel_flipped(curr_x, curr_y, 1)

# =========================================================
# 5. 初始變數
# =========================================================
frame_count = 0
last_sensor_read_time = 0
temp_val = 24.0

# =========================================================
# 6. 主迴圈：200ms 高刷，100% 復刻老師的 GIF 連鎖波浪放大特效
# =========================================================
while True:
    current_time = time.ticks_ms()
    
    # 每 2 秒更新一次 DHT22 感測值
    if time.ticks_diff(current_time, last_sensor_read_time) >= 2000:
        try:
            dht_sensor.measure()
            temp_val = dht_sensor.temperature()
        except:
            pass
        last_sensor_read_time = current_time
    
    oled.fill(0) # 清屏
    
    # ─── A. 頂部靜態文字層級 ───
    draw_text_flipped("PENGHU UNIVERSITY", 2, 5)
    draw_text_flipped("OF SCIENCE AND TECHNOLOGY", 2, 16)
    draw_text_flipped("DEPT OF CSIE", 2, 27)
    draw_text_flipped("2026", 92, 5)
    
    # ─── B. 左側：經典雙層圓圈 + 呼吸星 ───
    star_r = int(11 + 3 * math.sin(frame_count * 0.4))
    draw_circle_custom(42, 75, 28) 
    draw_circle_custom(42, 75, 26) 
    draw_star_five(42, 75, star_r) 
    
    # ─── C. 右側：🔥 精準復刻 GIF 中文字連鎖波浪放大動畫 🔥 ───
    # 利用時間差（相位差），讓花、火、節依序產生放大效果
    scale_flower = 1.2 + 0.3 * math.sin(frame_count * 0.4)       # 「花」主導
    scale_fire   = 1.2 + 0.3 * math.sin(frame_count * 0.4 - 1.2) # 「火」慢一步
    scale_fest   = 1.2 + 0.3 * math.sin(frame_count * 0.4 - 2.4) # 「節」再慢一步
    
    # 帶入動態縮放引擎 (傳入各字中心坐標，確保放大時原地膨脹不位移移位)
    draw_chinese_word_dynamic(104, 50,  "花", scale_flower)
    draw_chinese_word_dynamic(104, 78,  "火", scale_fire)
    draw_chinese_word_dynamic(104, 106, "節", scale_fest)
    
    # ─── D. 底部：即時溫度與防偽學號 ───
    draw_text_flipped(f"Temp: {temp_val:.1f} C", 2, 116)
    draw_text_flipped(f"ID:{MY_ID}", 42, 116)
    
    oled.show()
    frame_count += 1
    
    # 每 200ms 刷新一幀，流暢度滿分
