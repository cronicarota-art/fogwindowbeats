from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = '''    run_ffmpeg([
        "ffmpeg", "-y", "-stream_loop", "-1",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-t", str(duration),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p",
        "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-vsync", "cfr", "-an", str(output_path)
    ])
    concat_list.unlink(missing_ok=True)'''

new = '''    words = frase.encode("ascii","ignore").decode().split()
    drawtext_filters = []
    for i, word in enumerate(words):
        start = i * 0.4
        safe_word = word.replace("'", "").replace(":", "")
        drawtext_filters.append(
            f"drawtext=text='{safe_word}'"
            f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            f":fontsize=70:fontcolor=white@1.0"
            f":x=(w-text_w)/2:y=(h-text_h)/2+{i*80-len(words)*40}"
            f":enable='between(t,{start},{start+duration})'"
            f":alpha='if(lt(t-{start},0.3),(t-{start})/0.3,1)'"
            f":shadowcolor=black@0.8:shadowx=3:shadowy=3"
        )
    word_filter = ",".join(drawtext_filters) if drawtext_filters else "null"
    vf_v = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p,{word_filter}"
    run_ffmpeg([
        "ffmpeg", "-y", "-stream_loop", "-1",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-t", str(duration),
        "-vf", vf_v,
        "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-vsync", "cfr", "-an", str(output_path)
    ])
    concat_list.unlink(missing_ok=True)'''

if old in content:
    content = content.replace(old, new)
    filepath.write_text(content, encoding="utf-8")
    print("Texto animado word-by-word en shorts integrado")
else:
    print("ERROR: patron no encontrado")
    idx = content.find("scale=1080:1920")
    print(f"Contexto: {repr(content[max(0,idx-50):idx+150])}")