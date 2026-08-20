from pathlib import Path
filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")
content = content.replace('model="qwen/qwen3-27b"', 'model="qwen/qwen3.6-27b"')
filepath.write_text(content, encoding="utf-8")
print("Modelo actualizado a qwen/qwen3.6-27b")