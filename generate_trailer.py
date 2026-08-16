import pickle, subprocess, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

BASE = Path("C:/LofiZen")
ASSETS = BASE / "assets"

frames_dir = ASSETS / "trailer_frames"
frames_dir.mkdir(parents=True, exist_ok=True)

SCENES = [
    {"duration": 90, "text1": "FogWindowBeats", "text2": "lofi music 24/7", "bg": (8,6,20), "c1": (30,20,80), "c2": (20,50,120)},
    {"duration": 90, "text1": "Para estudiar", "text2": "sin distracciones", "bg": (8,6,20), "c1": (20,40,100), "c2": (40,80,160)},
    {"duration": 90, "text1": "Para trabajar", "text2": "con mas productividad", "bg": (6,8,20), "c1": (30,20,80), "c2": (60,30,120)},
    {"duration": 90, "text1": "Para relajarte", "text2": "y dormir mejor", "bg": (6,6,20), "c1": (20,20,80), "c2": (40,40,120)},
    {"duration": 90, "text1": "Suscribete!", "text2": "Nuevos videos todos los dias", "bg": (8,6,20), "c1": (60,30,120), "c2": (30,80,180)},
]

frame_idx = 0
for scene in SCENES:
    for i in range(scene["duration"]):
        progress = i / scene["duration"]
        img = Image.new("RGB", (1920,1080), color=scene["bg"])
        draw = ImageDraw.Draw(img)
        r1 = int(400 + progress * 50)
        draw.ellipse([(-100,-100),(r1,r1)], fill=scene["c1"])
        draw.ellipse([(1920-r1,1080-r1),(2100,1200)], fill=scene["c2"])
        alpha_text = min(int(progress * 3 * 255), 255)
        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
            font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
        except:
            font_big = ImageFont.load_default()
            font_med = font_big
        draw.text((960,460), scene["text1"], font=font_big, fill=(220,210,255), anchor="mm",
                  stroke_width=3, stroke_fill=(20,10,60))
        draw.text((960,580), scene["text2"], font=font_med, fill=(160,140,220), anchor="mm")
        draw.text((960,900), "FogWindowBeats", font=font_med, fill=(80,70,160), anchor="mm")
        img.save(str(frames_dir / f"frame_{frame_idx:05d}.jpg"), "JPEG", quality=85)
        frame_idx += 1

print(f"Frames generados: {frame_idx}")

audio_list = list((ASSETS/"audio_lofi").glob("*.mp3"))
if not audio_list:
    audio_list = list(ASSETS.glob("audio_small/*.mp3"))

subprocess.run([
    "ffmpeg", "-y",
    "-r", "30",
    "-i", str(frames_dir / "frame_%05d.jpg"),
    "-i", str(random.choice(audio_list)) if audio_list else "",
    "-c:v", "libx264", "-preset", "fast", "-crf", "24",
    "-c:a", "aac", "-b:a", "128k",
    "-t", "60",
    str(ASSETS / "trailer.mp4")
] if audio_list else [
    "ffmpeg", "-y",
    "-r", "30",
    "-i", str(frames_dir / "frame_%05d.jpg"),
    "-c:v", "libx264", "-preset", "fast", "-crf", "24",
    "-t", "60",
    str(ASSETS / "trailer.mp4")
], capture_output=False)

import shutil
shutil.rmtree(str(frames_dir))
print("Trailer generado: assets/trailer.mp4")

with open("token.pickle", "rb") as f:
    creds = pickle.load(f)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
service = build("youtube", "v3", credentials=creds)

media = MediaFileUpload(str(ASSETS/"trailer.mp4"), mimetype="video/mp4", resumable=True, chunksize=1024*1024*5)
request = service.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "FogWindowBeats - Lofi Music 24/7 para Estudiar, Trabajar y Relajarte",
            "description": "Bienvenido a FogWindowBeats, tu canal de lofi music 24/7.\n\nMusica lofi con lluvia, naturaleza y jazz para:\n- Estudiar sin distracciones\n- Trabajar con mas productividad\n- Relajarte y dormir mejor\n\nSuscribete y activa la campana para nuevos videos todos los dias.\n\n#lofi #musicapararelajarse #estudiar #lofihiphop #chillbeats",
            "tags": ["lofi", "lofi hip hop", "musica para estudiar", "chill beats", "study music", "lofi music", "FogWindowBeats"],
            "categoryId": "10",
            "defaultLanguage": "es"
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    },
    media_body=media
)
response = None
while response is None:
    _, response = request.next_chunk()
trailer_id = response["id"]
print(f"Trailer subido: https://youtu.be/{trailer_id}")

service.channels().update(
    part="brandingSettings",
    body={
        "id": "UCzcgxGQgTS8DbTvswp3OKqw",
        "brandingSettings": {
            "channel": {
                "unsubscribedTrailer": trailer_id,
                "description": "FogWindowBeats - Tu espacio de lofi 24/7\n\nMusica lofi con lluvia, naturaleza y jazz para estudiar, concentrarte, trabajar y relajarte.\n\nNuevos videos todos los dias.\n\nSuscribete y activa la campana!\n\n#lofi #musicapararelajarse #estudiar #concentracion #lofihiphop",
                "keywords": "lofi musica para estudiar concentracion lluvia lofi hip hop chill beats study music focus music lofi beats",
                "country": "CO"
            }
        }
    }
).execute()
print("Trailer configurado como trailer del canal")