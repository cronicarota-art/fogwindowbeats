from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = '''        "-vf", "scale=8000:4500:force_original_aspect_ratio=increase,zoompan=z='min(zoom+0.0003,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=24,format=yuv420p",'''

new = '''        "-vf", COLOR_GRADE.get(tipo, "") + (",scale=8000:4500:force_original_aspect_ratio=increase,zoompan=z='min(zoom+0.0003,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=24,format=yuv420p" if not COLOR_GRADE.get(tipo) else ",scale=8000:4500:force_original_aspect_ratio=increase,zoompan=z='min(zoom+0.0003,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=24," + COLOR_GRADE.get(tipo,"") + ",format=yuv420p"),'''

if old in content:
    content = content.replace(old, new)
    filepath.write_text(content, encoding="utf-8")
    print("Color grading integrado en build_video_horizontal")
else:
    print("ERROR: patron no encontrado")
    import re
    idx = content.find("scale=8000")
    print(f"Contexto en idx {idx}: {repr(content[max(0,idx-50):idx+100])}")