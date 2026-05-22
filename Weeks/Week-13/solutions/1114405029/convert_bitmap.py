from PIL import Image, ImageOps, ImageEnhance

INPUT_IMAGE = "goku.png"
OUTPUT_FILE = "goku_bitmap.py"

WIDTH = 56
HEIGHT = 56
THRESHOLD = 185

img = Image.open(INPUT_IMAGE).convert("L")

# 自動增加對比，讓五官和頭髮更明顯
img = ImageEnhance.Contrast(img).enhance(3.2)

# 裁切中央區域，避免整張圖塞進去太亂
w, h = img.size
crop_size = min(w, h)
left = (w - crop_size) // 2
top = (h - crop_size) // 2
img = img.crop((left, top, left + crop_size, top + crop_size))

# 縮小成 56x56，避免塞滿右側區域
img = img.resize((WIDTH, HEIGHT))

bitmap = []

for y in range(0, HEIGHT, 8):
    for x in range(WIDTH):
        byte = 0

        for bit in range(8):
            py = y + bit

            if py < HEIGHT:
                pixel = img.getpixel((x, py))

                # 深色才顯示，避免背景整片白
                if pixel < THRESHOLD:
                    byte |= (1 << bit)

        bitmap.append(byte)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("goku_width = {}\n".format(WIDTH))
    f.write("goku_height = {}\n\n".format(HEIGHT))
    f.write("goku_bitmap = bytearray([\n")

    for i, value in enumerate(bitmap):
        if i % 12 == 0:
            f.write("    ")
        f.write("0x{:02X}, ".format(value))
        if i % 12 == 11:
            f.write("\n")

    f.write("\n])\n")

print("Bitmap convert done")
print("Output file:", OUTPUT_FILE)
print("Size:", WIDTH, "x", HEIGHT)
print("Data length:", len(bitmap), "bytes")