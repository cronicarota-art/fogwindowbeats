from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = '''    overlay = ASSETS / "particle_overlay.png"
    if not vertical and overlay.exists():
        overlay_safe = str(overlay).replace("\\\\", "/").replace("\\", "/")
        vf = f"{wm},movie='{overlay_safe}'[ov];[in][ov]overlay=0:0"
    else:
        vf = wm'''

new = '''    overlay = ASSETS / "particle_overlay.png"
    if not vertical and overlay.exists():
        overlay_safe = str(overlay).replace("\\\\", "/")
        vf = wm + ",movie=" + overlay_safe + "[ov];[in][ov]overlay=0:0"
    else:
        vf = wm'''

if old in content:
    content = content.replace(old, new)
    filepath.write_text(content, encoding="utf-8")
    print("Fix overlay correcto")
else:
    print("ERROR: patron no encontrado")
    idx = content.find("particle_overlay")
    print(repr(content[max(0,idx-50):idx+300]))