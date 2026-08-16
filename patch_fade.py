from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = '''    run_ffmpeg([
        "ffmpeg", "-y", "-stream_loop", "-1",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-t", str(duration),
        "-vf", COLOR_GRADE.get(tipo, "") + (",scale=8000:4500:force_original_aspect_ratio=increase,zoompan=z=\'min(zoom+0.0003,1.3)\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d=1:s=1920x1080:fps=24,format=yuv420p" if not COLOR_GRADE.get(tipo) else ",scale=8000:4500:force_original_aspect_ratio=increase,zoompan=z=\'min(zoom+0.0003,1.3)\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d=1:s=1920x1080:fps=24," + COLOR_GRADE.get(tipo,"") + ",format=yuv420p"),
        "-r", "24", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30",
        "-vsync", "cfr", "-an", str(output_path)
    ])
    concat_list.unlink(missing_ok=True)

def build_video_vertical'''

new = '''    grade = COLOR_GRADE.get(tipo, "")
    vf_h = "scale=8000:4500:force_original_aspect_ratio=increase"
    vf_h += ",zoompan=z='min(zoom+0.0003,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=24"
    if grade:
        vf_h += f",{grade}"
    vf_h += ",format=yuv420p"
    vf_h += ",fade=t=in:st=0:d=1,fade=t=out:st={dur_fade}:d=1".format(dur_fade=max(0, duration-1))
    run_ffmpeg([
        "ffmpeg", "-y", "-stream_loop", "-1",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-t", str(duration),
        "-vf", vf_h,
        "-r", "24", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30",
        "-vsync", "cfr", "-an", str(output_path)
    ])
    concat_list.unlink(missing_ok=True)

def build_video_vertical'''

if old in content:
    content = content.replace(old, new)
    filepath.write_text(content, encoding="utf-8")
    print("Fade + color grading integrados correctamente")
else:
    print("ERROR: patron no encontrado")
    idx = content.find("COLOR_GRADE.get(tipo")
    print(f"Contexto: {repr(content[max(0,idx-20):idx+200])}")