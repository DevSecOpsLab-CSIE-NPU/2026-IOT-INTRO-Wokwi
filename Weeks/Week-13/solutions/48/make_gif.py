from pathlib import Path
from math import hypot

from PIL import Image, ImageDraw, ImageFilter


BASE = Path(__file__).with_name("image.png")
OUT = Path(__file__).with_name("wokwi_dynamic.gif")


def lerp(a, b, t):
    return a + (b - a) * t


def point_at_distance(points, distance):
    remaining = distance
    for start, end in zip(points, points[1:]):
        segment_length = hypot(end[0] - start[0], end[1] - start[1])
        if segment_length == 0:
            continue
        if remaining <= segment_length:
            ratio = remaining / segment_length
            return (lerp(start[0], end[0], ratio), lerp(start[1], end[1], ratio))
        remaining -= segment_length
    return points[-1]


def draw_wire_pulse(draw, points, color, frame, offset=0, span=26, width=4):
    total = 0
    lengths = []
    for start, end in zip(points, points[1:]):
        length = hypot(end[0] - start[0], end[1] - start[1])
        lengths.append(length)
        total += length

    if total == 0:
        return

    head = ((frame * 9) + offset) % total
    tail = (head - span) % total

    # Draw the wire highlight by sampling short points along the path.
    step = 4
    sample_count = max(1, int(span / step) + 2)
    for sample_index in range(sample_count):
        distance = (tail + sample_index * step) % total
        p = point_at_distance(points, distance)
        alpha = 220 if sample_index in (sample_count - 1, sample_count - 2) else 120
        draw.ellipse((p[0] - width, p[1] - width, p[0] + width, p[1] + width), fill=(*color, alpha))


def screen_glow(base, frame):
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Subtle activity on the OLED area only.
    draw.rectangle((113, 96, 286, 284), outline=(255, 255, 255, 20), width=1)
    for y in (112, 148, 184, 220, 256):
        alpha = 35 if frame % 6 < 3 else 12
        draw.line((118, y, 282, y), fill=(255, 255, 255, alpha), width=1)

    # A faint blinking marker near the lower-right corner.
    blink = 180 if frame % 8 < 4 else 35
    draw.ellipse((258, 226, 266, 234), fill=(255, 255, 255, blink))

    return overlay.filter(ImageFilter.GaussianBlur(0.4))


def build_frames():
    base = Image.open(BASE).convert("RGBA")
    w, h = base.size
    frames = []

    # Wire paths roughly matching the screenshot.
    red_path = [(92, 27), (320, 27), (320, 405), (257, 405), (257, 170), (160, 170), (160, 97)]
    green_path = [(76, 144), (433, 144), (433, 330), (114, 330), (114, 150), (160, 150)]
    blue_path = [(76, 123), (226, 123), (226, 167), (425, 167), (425, 404), (272, 404), (272, 188), (196, 188)]
    black_path = [(265, 146), (392, 146), (392, 404), (357, 404)]

    for frame in range(24):
        image = base.copy()
        draw = ImageDraw.Draw(image)

        # Gentle motion on the OLED screen.
        overlay = screen_glow(image, frame)
        image.alpha_composite(overlay)
        draw = ImageDraw.Draw(image)

        # Add moving glows to the existing wires.
        draw_wire_pulse(draw, red_path, (255, 40, 40), frame, offset=0, span=34, width=3)
        draw_wire_pulse(draw, green_path, (40, 255, 40), frame, offset=70, span=34, width=3)
        draw_wire_pulse(draw, blue_path, (60, 60, 255), frame, offset=140, span=34, width=3)
        draw_wire_pulse(draw, black_path, (150, 150, 150), frame, offset=210, span=24, width=2)

        # Tiny activity dots at the ESP32 and sensor edges.
        esp_blink = 200 if frame % 4 < 2 else 70
        sensor_blink = 200 if frame % 5 < 3 else 60
        draw.ellipse((70, 145, 75, 150), fill=(255, 255, 255, esp_blink))
        draw.ellipse((425, 162, 430, 167), fill=(255, 255, 255, sensor_blink))

        frames.append(image.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))

    return frames


def main():
    frames = build_frames()
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=90,
        loop=0,
        optimize=False,
    )
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
