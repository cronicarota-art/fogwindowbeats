from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

# Fix 1: modelo Groq actualizado
content = content.replace(
    'model="llama-3.3-70b-versatile"',
    'model="llama-3.1-8b-instant"'
)

# Fix 2: overlay PNG - hacerlo opcional con try/except en ffmpeg
old = '''    overlay = ASSETS / "particle_overlay.png"
    if not vertical and overlay.exists():
        vf = f"{wm},movie={str(overlay)}[ov];[in][ov]overlay=0:0"
    else:
        vf = wm'''

new = '''    overlay = ASSETS / "particle_overlay.png"
    if not vertical and overlay.exists():
        overlay_safe = str(overlay).replace("\\\\", "/").replace("\\", "/")
        vf = f"{wm},movie='{overlay_safe}'[ov];[in][ov]overlay=0:0"
    else:
        vf = wm'''

if old in content:
    content = content.replace(old, new)
    print("Fix overlay aplicado")
else:
    print("ERROR overlay: patron no encontrado")
    idx = content.find("particle_overlay")
    print(repr(content[max(0,idx-50):idx+200]))

filepath.write_text(content, encoding="utf-8")
print("Fix modelo Groq aplicado")