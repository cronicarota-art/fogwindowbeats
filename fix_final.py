from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

# Fix 1: quitar overlay completamente - es el problema del codigo 234
old = '''    overlay = ASSETS / "particle_overlay.png"
    if not vertical and overlay.exists():
        overlay_safe = str(overlay).replace("\\\\", "/")
        vf = wm + ",movie=" + overlay_safe + "[ov];[in][ov]overlay=0:0"
    else:
        vf = wm'''
new = '    vf = wm'

if old in content:
    content = content.replace(old, new)
    print("Fix overlay: removido")
else:
    print("ERROR overlay no encontrado")
    idx = content.find("particle_overlay")
    print(repr(content[max(0,idx-30):idx+200]))

# Fix 2: modelo Groq correcto
content = content.replace('model="llama-3.1-8b-instant"', 'model="qwen/qwen3-27b"')

filepath.write_text(content, encoding="utf-8")
print("Fix modelo: qwen/qwen3-27b")