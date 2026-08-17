from pathlib import Path
filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")
content = content.replace(
    "DURACIONES_LARGO = [7200, 10800, 14400, 21600, 28800]",
    "DURACIONES_LARGO = [3600, 5400, 7200]"
)
filepath.write_text(content, encoding="utf-8")
print("Duraciones reducidas: 1h, 1.5h, 2h")