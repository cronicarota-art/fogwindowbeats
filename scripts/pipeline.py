import os, random, pickle, subprocess, requests, json, glob, textwrap
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

TEST_MODE = os.environ.get("TEST_MODE", "0") == "1"

TIPOS = [
    "lofi_estudio", "lluvia_lofi", "jazz_lofi",
    "naturaleza", "lofi_dormir", "piano_relajante"
]

DURACIONES_LARGO = [7200, 10800, 14400, 21600, 28800]
DURACIONES_SHORT = [30, 45, 60]

AUDIO_MAP = {
    "lofi_estudio":    "audio_lofi",
    "lluvia_lofi":     "audio_lofi",
    "jazz_lofi":       "audio_lofi",
    "naturaleza":      "audio_lofi",
    "lofi_dormir":     "audio_lofi",
    "piano_relajante": "audio_piano"
}

FRASES_SHORT = [
    "cuando necesitas concentrarte Ã°Å¸Å½Â§",
    "la playlist perfecta para estudiar Ã°Å¸â€œÅ¡",
    "pon esto y desaparece del mundo Ã°Å¸Å’â„¢",
    "tu brain en modo focus Ã°Å¸Â§Â ",
    "lluvia + lofi = productividad infinita Ã°Å¸Å’Â§Ã¯Â¸Â",
    "el vibe que necesitas ahora mismo Ã¢Å“Â¨",
    "para cuando todo lo demÃƒÂ¡s falla Ã°Å¸Å½Âµ",
    "silencia el ruido, enciende el flow Ã°Å¸â€Â¥",
    "3am study session hits different Ã°Å¸Å’Æ’",
    "el soundtrack de tu mejor dia Ã°Å¸â€™Â«"
]

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
    folder = AUDIO_MAP[tipo]
    files = glob.glob(str(ASSETS / folder / "*.mp3"))
    files += glob.glob(str(ASSETS / folder / "*.wav"))
    return files

def get_video_files_h():
    files = glob.glob(str(ASSETS / "videos_lofi" / "*.mp4"))
    files += glob.glob(str(ASSETS / "videos_naturaleza" / "*.mp4"))
    files += glob.glob(str(ASSETS / "videos_lluvia" / "*.mp4"))
    return files

def get_video_files_v():
    return glob.glob(str(ASSETS / "videos_vertical" / "*.mp4"))

def run_ffmpeg(args):
    print(f"FFmpeg: {' '.join(str(a) for a in args)}")
    result = subprocess.run(args)
    if result.returncode != 0:
        raise Exception(f"FFmpeg fallo codigo {result.returncode}")

def build_audio(tipo, duration, output_path):
    audio_files = get_audio_files(tipo)
    if not audio_files:
        raise Exception(f"No hay audios para {tipo}")
    random.shuffle(audio_files)
    concat_list = BASE / "audio_concat.txt"
    selected = []
    total = 0
    while total < duration:
        for f in audio_files:
            selected.append(f)
            total += 180
            if total >= duration:
                break
    with open(concat_list, "w", encoding="utf-8") as f:
        for af in selected:
            f.write(f"file '{af}'\n")
    run_ffmpeg([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-t", str(duration),
        "-acodec", "aac", "-b:a", "128k",
        str(output_path)
    ])
    concat_list.unlink(missing_ok=True)

def build_video_horizontal(duration, output_path):
    video_files = get_video_files_h()
    if not video_files:
        raise Exception("No hay videos horizontales")
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
    run_ffmpeg([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-t", str(duration),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1",
        "-r", "24", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30",
        "-an", str(output_path)
    ])
    concat_list.unlink(missing_ok=True)

def build_video_vertical(duration, frase, output_path):
    video_files = get_video_files_v()
    if not video_files:
        raise Exception("No hay videos verticales")
    random.shuffle(video_files)
    concat_list = BASE / "video_concat_v.txt"
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
    run_ffmpeg([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-t", str(duration),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
        "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-an", str(output_path)
    ])
    concat_list.unlink(missing_ok=True)

def merge_av(video_path, audio_path, output_path):
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy", "-c:a", "copy",
        "-shortest", str(output_path)
    ])

def generate_metadata_largo(tipo, duration_h):
    client = Groq(api_key=GROQ_API_KEY)
    timestamps = ""
    for i in range(0, int(duration_h * 60), 15):
        h = i // 60
        m = i % 60
        timestamps += f"{h:02d}:{m:02d}:00 - Lofi Mix\n"
    prompt = f"""Genera metadata para YouTube, video de musica lofi tipo "{tipo}", duracion {duration_h} horas.
JSON con:
- titulo: max 80 chars, emoji, en espaÃƒÂ±ol, SEO agresivo (incluye duracion: "{duration_h} horas")
- descripcion: 400 palabras, incluye estos timestamps:\n{timestamps}\nhashtags al final
- tags: 20 tags en espaÃƒÂ±ol e ingles, lofi, estudio, concentracion, trabajar, dormir
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=1200
    )
    return json.loads(response.choices[0].message.content, strict=False)

def generate_metadata_short(tipo, frase):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""Genera metadata para un YouTube Short de musica lofi, tipo "{tipo}".
Frase del video: "{frase}"
JSON con:
- titulo: max 60 chars, viral, emoji, en espaÃƒÂ±ol, para Short de lofi
- descripcion: 3 lineas cortas + hashtags #lofi #shorts #estudiar #concentracion
- tags: 10 tags cortos lofi shorts
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=500
    )
    return json.loads(response.choices[0].message.content, strict=False)

def create_thumbnail_largo(tipo, titulo, duration_h, output_path):
    img = Image.new("RGB", (1280, 720), color=(8, 6, 20))
    draw = ImageDraw.Draw(img)
    colors = {
        "lofi_estudio":    [(50, 20, 150), (20, 120, 180)],
        "lluvia_lofi":     [(10, 40, 120), (40, 140, 200)],
        "jazz_lofi":       [(120, 50, 20), (180, 120, 20)],
        "naturaleza":      [(20, 80, 40), (40, 160, 80)],
        "lofi_dormir":     [(40, 10, 80), (80, 30, 120)],
        "piano_relajante": [(100, 30, 120), (160, 60, 180)]
    }
    c1, c2 = colors.get(tipo, [(50, 20, 150), (20, 120, 180)])
    for i in range(200):
        x = random.randint(0, 1280)
        y = random.randint(0, 720)
        r = random.randint(1, 3)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 255, random.randint(30, 100)))
    draw.ellipse([(-150, -150), (550, 550)], fill=c1)
    draw.ellipse([(750, 250), (1450, 950)], fill=c2)
    try:
        font_big = ImageFont.truetype("arial.ttf", 72)
        font_med = ImageFont.truetype("arial.ttf", 48)
        font_small = ImageFont.truetype("arial.ttf", 36)
    except:
        font_big = ImageFont.load_default()
        font_med = font_big
        font_small = font_big
    badge_text = f"{duration_h}H"
    draw.ellipse([(30, 30), (160, 160)], fill=(255, 200, 0))
    draw.text((95, 95), badge_text, font=font_med, fill=(20, 10, 50), anchor="mm",
              stroke_width=1, stroke_fill=(150, 100, 0))
    lines = textwrap.wrap(titulo.replace("Ã°Å¸â€œÅ¡","").replace("Ã°Å¸Å½Âµ","").replace("Ã°Å¸Å’â„¢","").replace("Ã°Å¸ËœÂ´","").replace("Ã°Å¸Å’Â¿","").replace("Ã¢Ëœâ€¢","").strip(), width=20)
    y = 220
    for line in lines[:3]:
        draw.text((640, y), line, font=font_big, fill=(255, 255, 255), anchor="mm",
                  stroke_width=3, stroke_fill=(0, 0, 0))
        y += 88
    etiquetas = {
        "lofi_estudio":    "Ã°Å¸â€œÅ¡ lofi para estudiar",
        "lluvia_lofi":     "Ã°Å¸Å’Â§Ã¯Â¸Â lluvia + lofi",
        "jazz_lofi":       "Ã°Å¸Å½Â· jazz lofi",
        "naturaleza":      "Ã°Å¸Å’Â¿ naturaleza relajante",
        "lofi_dormir":     "Ã°Å¸Å’â„¢ lofi para dormir",
        "piano_relajante": "Ã°Å¸Å½Â¹ piano relajante"
    }
    draw.rectangle([(0, 620), (1280, 720)], fill=(0, 0, 0, 180))
    draw.text((640, 655), etiquetas.get(tipo, "lofi beats"), font=font_med,
              fill=(200, 200, 255), anchor="mm")
    draw.text((1200, 700), "FogWindowBeats", font=font_small,
              fill=(150, 150, 200), anchor="rm")
    img.save(str(output_path), "JPEG", quality=95)

def create_thumbnail_short(tipo, frase, output_path):
    img = Image.new("RGB", (1080, 1920), color=(8, 6, 20))
    draw = ImageDraw.Draw(img)
    colors = {
        "lofi_estudio":    [(50, 20, 150), (20, 120, 180)],
        "lluvia_lofi":     [(10, 40, 120), (40, 140, 200)],
        "jazz_lofi":       [(120, 50, 20), (180, 120, 20)],
        "naturaleza":      [(20, 80, 40), (40, 160, 80)],
        "lofi_dormir":     [(40, 10, 80), (80, 30, 120)],
        "piano_relajante": [(100, 30, 120), (160, 60, 180)]
    }
    c1, c2 = colors.get(tipo, [(50, 20, 150), (20, 120, 180)])
    draw.ellipse([(-200, -200), (800, 800)], fill=c1)
    draw.ellipse([(400, 1200), (1400, 2200)], fill=c2)
    try:
        font_big = ImageFont.truetype("arial.ttf", 90)
        font_small = ImageFont.truetype("arial.ttf", 50)
    except:
        font_big = ImageFont.load_default()
        font_small = font_big
    lines = textwrap.wrap(frase, width=16)
    y = 800
    for line in lines:
        draw.text((540, y), line, font=font_big, fill=(255, 255, 255), anchor="mm",
                  stroke_width=4, stroke_fill=(0, 0, 0))
        y += 110
    draw.text((540, 1820), "FogWindowBeats", font=font_small,
              fill=(150, 150, 200), anchor="mm")
    img.save(str(output_path), "JPEG", quality=95)

def upload_youtube(service, video_path, thumbnail_path, metadata, is_short=False):
    body = {
        "snippet": {
            "title": metadata["titulo"],
            "description": metadata["descripcion"],
            "tags": metadata["tags"],
            "categoryId": "10",
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
    try:
        service.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
        ).execute()
    except Exception as te:
        print(f"Thumbnail omitido: {te}")
    return video_id

def pipeline_largo(tipo, service, tmp):
    duration = 60 if TEST_MODE else random.choice(DURACIONES_LARGO)
    duration_h = round(duration / 3600, 1) if not TEST_MODE else 0.016
    print(f"LARGO | tipo={tipo} | duracion={duration}s")
    audio_out = tmp / "audio.aac"
    video_raw = tmp / "video_raw.mp4"
    video_final = tmp / "video_final.mp4"
    thumbnail = tmp / "thumbnail.jpg"
    send_telegram(f"Ã°Å¸Å½Âµ LARGO iniciando\nTipo: {tipo} | {duration_h}h")
    build_audio(tipo, duration, audio_out)
    send_telegram("Ã°Å¸Å½Â¬ Construyendo video horizontal...")
    build_video_horizontal(duration, video_raw)
    send_telegram("Ã°Å¸â€â€” Mezclando AV...")
    merge_av(video_raw, audio_out, video_final)
    send_telegram("Ã°Å¸â€“Â¼ Metadata + thumbnail...")
    metadata = generate_metadata_largo(tipo, duration_h)
    create_thumbnail_largo(tipo, metadata["titulo"], duration_h, thumbnail)
    send_telegram("Ã°Å¸â€œÂ¤ Subiendo a YouTube...")
    video_id = upload_youtube(service, video_final, thumbnail, metadata)
    for f in [audio_out, video_raw, video_final, thumbnail]:
        try: f.unlink()
        except: pass
    return video_id, metadata["titulo"]

def pipeline_short(tipo, service, tmp):
    duration = 30 if TEST_MODE else random.choice(DURACIONES_SHORT)
    frase = random.choice(FRASES_SHORT)
    print(f"SHORT | tipo={tipo} | duracion={duration}s | frase={frase}")
    audio_out = tmp / "audio_s.aac"
    video_raw = tmp / "video_raw_s.mp4"
    video_final = tmp / "video_final_s.mp4"
    thumbnail = tmp / "thumbnail_s.jpg"
    send_telegram(f"Ã°Å¸â€œÂ± SHORT iniciando\nFrase: {frase}")
    build_audio(tipo, duration, audio_out)
    send_telegram("Ã°Å¸Å½Â¬ Construyendo video vertical...")
    build_video_vertical(duration, frase, video_raw)
    send_telegram("Ã°Å¸â€â€” Mezclando AV...")
    merge_av(video_raw, audio_out, video_final)
    send_telegram("Ã°Å¸â€“Â¼ Metadata + thumbnail...")
    metadata = generate_metadata_short(tipo, frase)
    create_thumbnail_short(tipo, frase, thumbnail)
    send_telegram("Ã°Å¸â€œÂ¤ Subiendo Short...")
    video_id = upload_youtube(service, video_final, thumbnail, metadata, is_short=True)
    for f in [audio_out, video_raw, video_final, thumbnail]:
        try: f.unlink()
        except: pass
    return video_id, metadata["titulo"]

def main():
    tipo = random.choice(TIPOS)
    modo = random.choices(["largo", "short"], weights=[60, 40])[0]
    if TEST_MODE:
        modo = os.environ.get("MODO", "largo")
    send_telegram(f"Ã°Å¸Å¡â‚¬ FogWindowBeats arrancando\nModo: {modo.upper()} | Tipo: {tipo}")
    tmp = BASE / "tmp"
    tmp.mkdir(exist_ok=True)
    service = get_youtube_service()
    try:
        if modo == "largo":
            video_id, titulo = pipeline_largo(tipo, service, tmp)
        else:
            video_id, titulo = pipeline_short(tipo, service, tmp)
        url = f"https://youtu.be/{video_id}"
        if modo == "short":
            url = f"https://youtube.com/shorts/{video_id}"
        send_telegram(f"Ã¢Å“â€¦ Publicado [{modo.upper()}]\n{titulo}\n{url}")
        print(f"Ã¢Å“â€¦ {url}")
    except Exception as e:
        send_telegram(f"Ã¢ÂÅ’ Error FogWindowBeats: {e}")
        print(f"ERROR: {e}")
        raise

if __name__ == "__main__":
    main()