from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = """def create_thumbnail_largo(tipo, titulo, duration_h, video_path, output_path):"""

new = """AB_STYLE = ["cinematic", "minimal"]

def create_thumbnail_largo(tipo, titulo, duration_h, video_path, output_path, style=None):
    if style is None:
        import random
        style = random.choice(AB_STYLE)
    print(f"Thumbnail style: {style}")"""

if old in content:
    content = content.replace(old, new)
    filepath.write_text(content, encoding="utf-8")
    print("A/B testing agregado")
else:
    print("ERROR: patron no encontrado")