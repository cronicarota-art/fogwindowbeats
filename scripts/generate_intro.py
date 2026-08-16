from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess

def generate_intro(output_path="assets/intro.mp4"):
    frames_dir = Path("assets/intro_frames")
    frames_dir.mkdir(parents=True, exist_ok=True)
    for i in range(72):
        img = Image.new("RGB", (1920, 1080), color=(8, 6, 20))
        draw = ImageDraw.Draw(img)
        progress = i / 72.0
        alpha = int(min(progress * 3, 1.0) * 255)
        scale = 0.7 + progress * 0.3
        cx, cy = 960, 480
        r = int(120 * scale)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(30, 20, 80))
        draw.ellipse([cx-r+4, cy-r+4, cx+r-4, cy+r-4], outline=(100, 80, 200), width=3)
        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            font_big = ImageFont.load_default()
            font_small = font_big
        text_alpha = min(int(progress * 4 * 255), 255)
        draw.text((cx, cy - 20), "FogWindow", font=font_big, fill=(200, 180, 255), anchor="mm")
        draw.text((cx, cy + 50), "BEATS", font=font_small, fill=(120, 100, 200), anchor="mm")
        draw.text((cx, 900), "lofi music 24/7", font=font_small, fill=(80, 80, 160), anchor="mm")
        img.save(str(frames_dir / f"frame_{i:04d}.jpg"), "JPEG", quality=90)
    subprocess.run([
        "ffmpeg", "-y", "-r", "24",
        "-i", str(frames_dir / "frame_%04d.jpg"),
        "-c:v", "libx264", "-preset", "fast", "-crf", "28",
        "-t", "3", output_path
    ], capture_output=True)
    import shutil
    shutil.rmtree(str(frames_dir))
    print(f"Intro generada: {output_path}")

generate_intro()