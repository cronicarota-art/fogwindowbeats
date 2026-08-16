from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = "def build_video_vertical(tipo, duration, output_path):"
new = "def build_video_vertical(tipo, duration, output_path, frase=''):"

if old in content:
    content = content.replace(old, new)
    filepath.write_text(content, encoding="utf-8")
    print("Firma build_video_vertical corregida")
else:
    print("ERROR: no encontrado")