from machine import Pin, I2C
import ssd1306
import math
import time

# I2C setup for SSD1306 OLED (ESP32)
# SCL=22, SDA=21 are standard for the provided diagram.json
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def draw_circle(cx, cy, r, color=1):
    """Draw a simple circle using Midpoint Circle Algorithm."""
    x = r
    y = 0
    err = 0
    while x >= y:
        oled.pixel(cx + x, cy + y, color)
        oled.pixel(cx + y, cy + x, color)
        oled.pixel(cx - y, cy + x, color)
        oled.pixel(cx - x, cy + y, color)
        oled.pixel(cx - x, cy - y, color)
        oled.pixel(cx - y, cy - x, color)
        oled.pixel(cx + y, cy - x, color)
        oled.pixel(cx + x, cy - y, color)
        y += 1
        if err <= 0:
            err += 2 * y + 1
        else:
            x -= 1
            err += 2 * (y - x) + 1

def draw_star(cx, cy, r, angle, color=1):
    """Draw a rotating pentagram (5-pointed star)."""
    points = []
    for i in range(5):
        # 144 degrees skip for pentagram pattern
        theta = math.radians(i * 144 + angle - 90)
        points.append((int(cx + r * math.cos(theta)), int(cy + r * math.sin(theta))))
    
    for i in range(5):
        p1 = points[i]
        p2 = points[(i + 1) % 5]
        oled.line(p1[0], p1[1], p2[0], p2[1], color)

def draw_dragon_balls(cx, cy, r_orbit, angle):
    """Draw 7 'Dragon Balls' orbiting on a circle."""
    for i in range(7):
        theta = math.radians(i * (360/7) + angle)
        bx = int(cx + r_orbit * math.cos(theta))
        by = int(cy + r_orbit * math.sin(theta))
        # Draw a small 3x3 ball with a center hole
        oled.fill_rect(bx - 1, by - 1, 3, 3, 1)
        oled.pixel(bx, by, 0)

def draw_csie_wave(frame):
    """Draw 'CSIE' text with a wave animation."""
    text = "CSIE"
    x_start = 10
    y_base = 45
    for i, char in enumerate(text):
        # Wave movement: each letter has a different phase
        y_off = int(6 * math.sin(math.radians(frame * 15 + i * 50)))
        oled.text(char, x_start + i * 12, y_base + y_off, 1)

def main():
    frame = 0
    print("Starting OLED Animation...")
    
    while True:
        # Clear screen
        oled.fill(0)
        
        # 1. 左側英文小字資訊 (Left-side Info)
        oled.text("ID:1114405035", 0, 0, 1)
        oled.text("IoT Task 2a", 0, 10, 1)
        oled.text("ESP32-Wokwi", 0, 20, 1)
        
        # 2. 右上角 2026
        oled.text("2026", 95, 0, 1)
        
        # Center coordinates for star and balls
        cx, cy = 85, 35
        
        # 3. 旋轉五芒星 + 呼吸效果 (Rotating Star with Breathing)
        # Radius cycles between 11 and 19
        star_r = 15 + 4 * math.sin(math.radians(frame * 10))
        draw_star(cx, cy, star_r, frame * 8, 1)
        
        # 4. 外圓龍珠 (Outer Circle Dragon Balls)
        r_orbit = 26
        draw_circle(cx, cy, r_orbit, 1) # The orbit path
        draw_dragon_balls(cx, cy, r_orbit, -frame * 4)
        
        # 5. CSIE 波浪舞動畫 (CSIE Wave)
        draw_csie_wave(frame)
        
        # 6. 直排閃爍動畫 (Vertical Flash Placeholder for 花火節)
        chars = ["H", "H", "J"]
        flash_idx = (frame // 10) % 3
        for i, c in enumerate(chars):
            if i == flash_idx:
                # Flash effect: inverted color
                oled.fill_rect(100, 15 + i*14, 12, 12, 1)
                oled.text(c, 102, 17 + i*14, 0)
            else:
                oled.text(c, 102, 17 + i*14, 1)

        # Render frame
        oled.show()
        
        # Update frame counter and sleep
        frame = (frame + 1) % 360
        time.sleep_ms(30)

if __name__ == "__main__":
    main()
