from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = "    build_video_vertical(tipo, duration, video_raw)"
new = "    build_video_vertical(tipo, duration, video_raw, frase=frase)"

if old in content:
    content = content.replace(old, new)
    filepath.write_text(content, encoding="utf-8")
    print("Llamada build_video_vertical corregida con frase")
else:
    print("ERROR: no encontrado")