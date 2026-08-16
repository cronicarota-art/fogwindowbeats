from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = '''    vf_h = "scale=8000:4500:force_original_aspect_ratio=increase"
    vf_h += ",zoompan=z='min(zoom+0.0003,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=24"
    if grade:
        vf_h += f",{grade}"
    vf_h += ",format=yuv420p"
    vf_h += ",fade=t=in:st=0:d=1,fade=t=out:st={dur_fade}:d=1".format(dur_fade=max(0, duration-1))'''

new = '''    vf_h = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1"
    if grade:
        vf_h += f",{grade}"
    vf_h += ",fps=24,format=yuv420p"'''

if old in content:
    content = content.replace(old, new)
    filepath.write_text(content, encoding="utf-8")
    print("Zoompan removido - pipeline rapido")
else:
    print("ERROR: patron no encontrado")
    idx = content.find("zoompan")
    print(repr(content[max(0,idx-100):idx+200]))