import random
from PIL import Image, ImageDraw
from pathlib import Path

def generate_particle_overlay(width=1920, height=1080, output_path="assets/particle_overlay.png"):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for _ in range(80):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(1, 3)
        alpha = random.randint(30, 100)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 255, alpha))
    for _ in range(30):
        x = random.randint(0, width)
        y = random.randint(0, height)
        length = random.randint(10, 30)
        alpha = random.randint(20, 60)
        draw.line([(x, y), (x-2, y+length)], fill=(200, 220, 255, alpha), width=1)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Overlay generado: {output_path}")

generate_particle_overlay()