from machine import Pin, SPI
import ili9341
from fonts import draw_title

# Hardware Configuration
SPI_SCK = 18
SPI_MOSI = 23
TFT_CS = 5
TFT_DC = 17

# Color for student 1114405022: Yellow ("黃")
YELLOW = 0xE0FF 
BLACK = 0x0000

# Initialize SPI and ILI9341
spi = SPI(2, baudrate=40_000_000, sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI))
cs = Pin(TFT_CS, Pin.OUT)
dc = Pin(TFT_DC, Pin.OUT)
display = ili9341.ILI9341(spi, cs=cs, dc=dc)

def main():
    print("--- Program Starting ---")
    print(f"Using Color: {hex(YELLOW)}")
    # Clear screen
    print("Clearing screen...")
    display.fill(BLACK)
    
    # 標題：「大城北游泳池空汙偵測」
    # 依照要求書：5字 x 2列，水平置中
    # x = (240 - 5 * 32) / 2 = 40
    print("Drawing title (5x2 centered) in YELLOW...")
    draw_title(display, x=40, y=100, color=YELLOW, scale=1, per_row=5)
    print("--- Drawing Finished ---")

if __name__ == "__main__":
    main()
