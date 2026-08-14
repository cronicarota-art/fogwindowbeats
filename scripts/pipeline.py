import os, sys, random, pickle, datetime, subprocess, requests, json, glob, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from groq import Groq
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

BASE = Path(__file__).parent.parent
ASSETS = BASE / "assets"
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

TIPOS = [
    "lofi_estudio",
    "lluvia_lofi",
    "jazz_lofi",
    "naturaleza",
    "lofi_dormir",
    "piano_relajante"
]

AUDIO_MAP = {
    "lofi_estudio":   "audio_lofi",
    "lluvia_lofi":    ["audio_lofi", "audio_lluvia"],
    "jazz_lofi":      "audio_jazz",
    "naturaleza":     "audio_naturaleza",
    "lofi_dormir":    "audio_lofi",
    "piano_relajante":"audio_piano"
}

VIDEO_MAP = {
    "lofi_estudio":   "videos_lofi",
    "lluvia_lofi":    "videos_lluvia",
    "jazz_lofi":      "videos_lofi",
    "naturaleza":     "videos_naturaleza",
    "lofi_dormir":    "videos_lofi",
    "piano_relajante":"videos_naturaleza"
}

TARGET_DURATION = random.randint(3600, 5400)

def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}
        )
    except:
        pass

def get_youtube_service():
    token_path = BASE / "token.pickle"
    with open(token_path, "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)

def get_audio_files(tipo):
    mapping = AUDIO_MAP[tipo]
    files = []
    if isinstance(mapping, list):
        for folder in mapping:
            files += glob.glob(str(ASSETS / folder / "*.mp3"))
            files += glob.glob(str(ASSETS / folder / "*.wav"))
    else:
        files += glob.glob(str(ASSETS / mapping / "*.mp3"))
        files += glob.glob(str(ASSETS / mapping / "*.wav"))
    return files

def get_video_files(tipo):
    folder = VIDEO_MAP[tipo]
    files = glob.glob(str(ASSETS / folder / "*.mp4"))
    files += glob.glob(str(ASSETS / folder / "*.mov"))
    return files

def build_audio(tipo, output_path):
    audio_files = get_audio_files(tipo)
    if not audio_files:
        raise Exception(f"No hay archivos de audio en {AUDIO_MAP[tipo]}")
    random.shuffle(audio_files)
    concat_list = BASE / "audio_concat.txt"
    total = 0
    selected = []
    while total < TARGET_DURATION:
        for f in audio_files:
            selected.append(f)
            total += 180
            if total >= TARGET_DURATION:
                break
    with open(concat_list, "w", encoding="utf-8") as f:
        for af in selected:
            f.write(f"file '{af}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-t", str(TARGET_DURATION),
        "-acodec", "aac", "-b:a", "128k",
        str(output_path)
    ], check=True, capture_output=True)
    concat_list.unlink(missing_ok=True)

def build_video_loop(tipo, duration, output_path):
    video_files = get_video_files(tipo)
    if not video_files:
        raise Exception(f"No hay archivos de video en {VIDEO_MAP[tipo]}")
    random.shuffle(video_files)
    concat_list = BASE / "video_concat.txt"
    selected = []
    total = 0
    while total < duration:
        for f in video_files:
            selected.append(f)
            total += 30
            if total >= duration:
                break
    with open(concat_list, "w", encoding="utf-8") as f:
        for vf in selected:
            f.write(f"file '{vf}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-t", str(duration),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1",
        "-r", "24", "-c:v", "libx264", "-preset", "fast", "-crf", "28",
        "-an", str(output_path)
    ], check=True, capture_output=True)
    concat_list.unlink(missing_ok=True)

def merge_av(video_path, audio_path, output_path):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy", "-c:a", "copy",
        "-shortest", str(output_path)
    ], check=True, capture_output=True)

def generate_metadata(tipo):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""Genera metadata para un video de YouTube de musica lofi tipo "{tipo}".
Responde SOLO con JSON con estas claves:
- titulo: string llamativo con emoji, max 80 chars, en español, optimizado SEO
- descripcion: string de 300 palabras con timestamps cada 15 min, hashtags lofi al final
- tags: lista de 15 strings en español e ingles sobre lofi, concentracion, musica para estudiar
Tipo de contenido: {tipo}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=1000
    )
    return json.loads(response.choices[0].message.content, strict=False)

def create_thumbnail(tipo, titulo, output_path):
    img = Image.new("RGB", (1280, 720), color=(10, 8, 25))
    draw = ImageDraw.Draw(img)
    for i in range(0, 1280, 40):
        alpha = random.randint(10, 40)
        draw.line([(i, 0), (i+20, 720)], fill=(100, 60, 200, alpha), width=1)
    colors = {
        "lofi_estudio":   [(80, 40, 180), (40, 180, 220)],
        "lluvia_lofi":    [(30, 80, 180), (80, 200, 255)],
        "jazz_lofi":      [(180, 80, 40), (220, 160, 40)],
        "naturaleza":     [(40, 140, 80), (80, 220, 120)],
        "lofi_dormir":    [(60, 30, 120), (120, 60, 180)],
        "piano_relajante":[(140, 60, 160), (200, 100, 220)]
    }
    c1, c2 = colors.get(tipo, [(80, 40, 180), (40, 180, 220)])
    draw.ellipse([(-100, -100), (500, 500)], fill=c1+(30,) if len(c1)==3 else c1)
    draw.ellipse([(800, 300), (1400, 900)], fill=c2+(25,) if len(c2)==3 else c2)
    try:
        font_big = ImageFont.truetype("arial.ttf", 80)
        font_small = ImageFont.truetype("arial.ttf", 45)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()
    lines = textwrap.wrap(titulo, width=22)
    y = 200
    for line in lines[:3]:
        draw.text((640, y), line, font=font_big, fill=(255,255,255), anchor="mm",
                  stroke_width=3, stroke_fill=(0,0,0))
        y += 95
    etiquetas = {
        "lofi_estudio":   "lofi para estudiar",
        "lluvia_lofi":    "lluvia + lofi",
        "jazz_lofi":      "jazz lofi",
        "naturaleza":     "naturaleza relajante",
        "lofi_dormir":    "lofi para dormir",
        "piano_relajante":"piano relajante"
    }
    draw.text((640, 620), etiquetas.get(tipo,"lofi beats"), font=font_small,
              fill=(180,180,255), anchor="mm")
    draw.text((640, 670), "FogWindowBeats", font=font_small,
              fill=(120,120,200), anchor="mm")
    img.save(str(output_path), "JPEG", quality=95)

def upload_youtube(service, video_path, thumbnail_path, metadata, tipo):
    categorias = {
        "lofi_estudio": "10", "lluvia_lofi": "10", "jazz_lofi": "10",
        "naturaleza": "10", "lofi_dormir": "10", "piano_relajante": "10"
    }
    body = {
        "snippet": {
            "title": metadata["titulo"],
            "description": metadata["descripcion"],
            "tags": metadata["tags"],
            "categoryId": categorias.get(tipo, "10"),
            "defaultLanguage": "es"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4",
                            resumable=True, chunksize=1024*1024*5)
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response["id"]
    service.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
    ).execute()
    return video_id

def main():
    tipo = random.choice(TIPOS)
    send_telegram(f"🎵 FogWindowBeats iniciando\nTipo: {tipo}")
    tmp = BASE / "tmp"
    tmp.mkdir(exist_ok=True)
    audio_out = tmp / "audio.aac"
    video_raw = tmp / "video_raw.mp4"
    video_final = tmp / "video_final.mp4"
    thumbnail = tmp / "thumbnail.jpg"
    try:
        send_telegram("🔊 Construyendo audio...")
        build_audio(tipo, audio_out)
        send_telegram("🎬 Construyendo video loop...")
        build_video_loop(tipo, TARGET_DURATION, video_raw)
        send_telegram("🔗 Mezclando audio y video...")
        merge_av(video_raw, audio_out, video_final)
        send_telegram("🖼 Generando metadata y thumbnail...")
        metadata = generate_metadata(tipo)
        create_thumbnail(tipo, metadata["titulo"], thumbnail)
        send_telegram("📤 Subiendo a YouTube...")
        service = get_youtube_service()
        video_id = upload_youtube(service, video_final, thumbnail, metadata, tipo)
        msg = f"""✅ FogWindowBeats publicado
Tipo: {tipo}
Titulo: {metadata['titulo']}
URL: https://youtu.be/{video_id}"""
        send_telegram(msg)
    except Exception as e:
        send_telegram(f"❌ FogWindowBeats error: {e}")
        raise
    finally:
        for f in [audio_out, video_raw, video_final, thumbnail]:
            try: f.unlink()
            except: pass

if __name__ == "__main__":
    main()