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

TIPOS = ["lofi_estudio", "lluvia_lofi", "jazz_lofi", "naturaleza", "lofi_dormir", "piano_relajante"]

DURACIONES_LARGO = [7200, 10800, 14400, 21600, 28800]
DURACIONES_SHORT = [15, 30, 45, 60]

AUDIO_MAP = {
    "lofi_estudio":    "audio_lofi",
    "lluvia_lofi":     "audio_lofi",
    "jazz_lofi":       "audio_lofi",
    "naturaleza":      "audio_lofi",
    "lofi_dormir":     "audio_lofi",
    "piano_relajante": "audio_piano"
}

VIDEO_MAP = {
    "lofi_estudio":    "videos_lofi",
    "lluvia_lofi":     "videos_lluvia",
    "jazz_lofi":       "videos_lofi",
    "naturaleza":      "videos_naturaleza",
    "lofi_dormir":     "videos_lofi",
    "piano_relajante": "videos_naturaleza"
}

FRASES_SHORT = [
    "cuando necesitas concentrarte",
    "la playlist perfecta para estudiar",
    "pon esto y desaparece del mundo",
    "tu brain en modo focus",
    "lluvia para concentrarse",
    "el vibe que necesitas ahora mismo",
    "para cuando todo lo demas falla",
    "silencia el ruido enciende el flow",
    "3am study session hits different",
    "el soundtrack de tu mejor dia"
]

ETIQUETAS = {
    "lofi_estudio":    "lofi para estudiar",
    "lluvia_lofi":     "lluvia + lofi",
    "jazz_lofi":       "jazz lofi",
    "naturaleza":      "naturaleza relajante",
    "lofi_dormir":     "lofi para dormir",
    "piano_relajante": "piano relajante"
}

def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=10
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

def get_video_files(tipo):
    env_folder = os.environ.get("VIDEO_TIPO_H")
    if env_folder and Path(env_folder).exists():
        files = glob.glob(f"{env_folder}/*.mp4")
        if files:
            return files
    folder = VIDEO_MAP[tipo]
    files = glob.glob(str(ASSETS / folder / "*.mp4"))
    return files

def get_video_files_vertical():
    env_folder = os.environ.get("VIDEO_TIPO_V")
    if env_folder and Path(env_folder).exists():
        files = glob.glob(f"{env_folder}/*.mp4")
        if files:
            return files
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

def build_video_horizontal(tipo, duration, output_path):
    video_files = get_video_files(tipo)
    if not video_files:
        raise Exception(f"No hay videos para {tipo}")
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

def build_video_vertical(tipo, duration, output_path):
    video_files = get_video_files_vertical()
    if not video_files:
        video_files = get_video_files(tipo)
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

def extract_frame(video_path, output_path, width, height):
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-ss", "00:00:03",
        "-vframes", "1",
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
        str(output_path)
    ])

def create_thumbnail_largo(tipo, titulo, duration_h, video_path, output_path):
    frame_path = output_path.parent / "frame_tmp.jpg"
    try:
        extract_frame(video_path, frame_path, 1280, 720)
        img = Image.open(str(frame_path)).convert("RGB")
        img = img.resize((1280, 720))
    except:
        img = Image.new("RGB", (1280, 720), color=(10, 8, 25))
    draw = ImageDraw.Draw(img)
    overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 140))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        font_big = ImageFont.load_default()
        font_med = font_big
        font_small = font_big
    badge = f"{duration_h}H"
    draw.ellipse([(30, 25), (130, 125)], fill=(255, 200, 0))
    draw.text((80, 75), badge, font=font_med, fill=(20, 10, 50), anchor="mm")
    titulo_clean = titulo.encode("ascii", "ignore").decode()
    lines = textwrap.wrap(titulo_clean, width=22)
    y = 220
    for line in lines[:3]:
        draw.text((640, y), line, font=font_big, fill=(255, 255, 255), anchor="mm",
                  stroke_width=3, stroke_fill=(0, 0, 0))
        y += 90
    draw.rectangle([(0, 630), (1280, 720)], fill=(0, 0, 0, 200))
    etiqueta = ETIQUETAS.get(tipo, "lofi beats")
    draw.text((640, 675), etiqueta, font=font_med, fill=(200, 220, 255), anchor="mm")
    draw.text((1240, 710), "FogWindowBeats", font=font_small, fill=(150, 150, 200), anchor="rm")
    img.save(str(output_path), "JPEG", quality=95)
    if frame_path.exists():
        frame_path.unlink()

def create_thumbnail_short(tipo, frase, video_path, output_path):
    frame_path = output_path.parent / "frame_s_tmp.jpg"
    try:
        extract_frame(video_path, frame_path, 1080, 1920)
        img = Image.open(str(frame_path)).convert("RGB")
        img = img.resize((1080, 1920))
    except:
        img = Image.new("RGB", (1080, 1920), color=(10, 8, 25))
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 120))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
    except:
        font_big = ImageFont.load_default()
        font_small = font_big
    frase_clean = frase.encode("ascii", "ignore").decode()
    lines = textwrap.wrap(frase_clean, width=18)
    y = 820
    for line in lines:
        draw.text((540, y), line, font=font_big, fill=(255, 255, 255), anchor="mm",
                  stroke_width=4, stroke_fill=(0, 0, 0))
        y += 100
    draw.text((540, 1860), "FogWindowBeats", font=font_small, fill=(180, 180, 255), anchor="mm")
    img.save(str(output_path), "JPEG", quality=95)
    if frame_path.exists():
        frame_path.unlink()

def generate_metadata_largo(tipo, duration_h):
    client = Groq(api_key=GROQ_API_KEY)
    timestamps = ""
    mins = int(duration_h * 60)
    for i in range(0, mins, 15):
        h = i // 60
        m = i % 60
        timestamps += f"{h:02d}:{m:02d}:00 - Lofi Mix\n"
    prompt = f"""Eres un experto en SEO y marketing de YouTube especializado en musica lofi y ambience.
Genera metadata VIRAL para un video de YouTube tipo "{tipo}", duracion {duration_h} horas.

REGLAS PARA EL TITULO:
- Maximo 80 caracteres
- Debe ser IRRESISTIBLE, emocional, que la gente quiera hacer clic
- Incluye la duracion exacta: {duration_h} horas
- Usa emojis relevantes al tema (lluvia=, piano=, naturaleza=, dormir=, estudio=)
- Ejemplos de estilo BUENO: "3 Horas de Lluvia + Lofi para Estudiar Sin Parar", "Lluvia en la Ventana  - 4 Horas de Lofi Perfecto para Concentrarse", "No Podras Dejar de Estudiar con Este Lofi  - 2 Horas"
- Ejemplos de estilo MALO (evitar): "Musica Lofi para Estudiar 3.0 horas", "Lofi Mix 2 horas"

TIPO DE CONTENIDO: {tipo}
EMOCIONES A TRANSMITIR segun tipo:
- lofi_estudio: concentracion, productividad, cafe, madrugada, focus
- lluvia_lofi: lluvia en ventana, cozy, tormenta perfecta, noche lluviosa
- jazz_lofi: elegancia, cafe parisino, noche de jazz, smooth
- naturaleza: paz, bosque, aire fresco, desconectar
- lofi_dormir: relajacion profunda, dormir bien, mente en calma
- piano_relajante: belleza, emocion, piano suave, alma

JSON con:
- titulo: string viral segun reglas
- descripcion: 500 palabras, emocionante, incluye beneficios (concentracion, relajacion, etc), timestamps:\n{timestamps}\nhashtags relevantes al final (minimo 15)
- tags: lista de 25 tags SEO agresivos en espanol e ingles
"""
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=1200
    )
    return json.loads(r.choices[0].message.content, strict=False)

def generate_metadata_short(tipo, frase):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""Eres experto en YouTube Shorts virales de musica lofi.
Genera metadata para un Short tipo "{tipo}", frase central: "{frase}"

REGLAS TITULO:
- Maximo 60 chars, debe generar curiosidad o identificacion inmediata
- Ejemplos BUENOS: "POV: son las 3am y tienes que entregar", "cuando el lofi te salva la vida", "la lluvia perfecta para concentrarse"
- Usa minusculas estilo casual, emojis al final

JSON con:
- titulo: string viral casual en espanol
- descripcion: 2 lineas emotivas + hashtags #lofi #shorts #estudiar #concentracion #fyp #parati
- tags: lista de 15 tags cortos lofi shorts viral
"""
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=500
    )
    return json.loads(r.choices[0].message.content, strict=False)

def upload_youtube(service, video_path, thumbnail_path, metadata):
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
    except Exception as e:
        print(f"Thumbnail omitido: {e}")
    return video_id

def pipeline_largo(tipo, service, tmp):
    duration = random.choice(DURACIONES_LARGO)
    duration_h = round(duration / 3600, 1)
    print(f"LARGO | tipo={tipo} | {duration_h}h")
    audio_out = tmp / "audio.aac"
    video_raw = tmp / "video_raw.mp4"
    video_final = tmp / "video_final.mp4"
    thumbnail = tmp / "thumbnail.jpg"
    send_telegram(f"ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â½ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Âµ LARGO iniciando\nTipo: {tipo} | {duration_h}h")
    build_audio(tipo, duration, audio_out)
    send_telegram("ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â½ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ Construyendo video...")
    build_video_horizontal(tipo, duration, video_raw)
    send_telegram("ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚ÂÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â Mezclando AV...")
    merge_av(video_raw, audio_out, video_final)
    send_telegram("ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¼ Metadata + thumbnail...")
    metadata = generate_metadata_largo(tipo, duration_h)
    create_thumbnail_largo(tipo, metadata["titulo"], duration_h, video_raw, thumbnail)
    send_telegram("ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¤ Subiendo a YouTube...")
    video_id = upload_youtube(service, video_final, thumbnail, metadata)
    for f in [audio_out, video_raw, video_final, thumbnail]:
        try: f.unlink()
        except: pass
    return video_id, metadata["titulo"]

def pipeline_short(tipo, service, tmp):
    duration = random.choice(DURACIONES_SHORT)
    frase = random.choice(FRASES_SHORT)
    print(f"SHORT | tipo={tipo} | {duration}s | frase={frase}")
    audio_out = tmp / "audio_s.aac"
    video_raw = tmp / "video_raw_s.mp4"
    video_final = tmp / "video_final_s.mp4"
    thumbnail = tmp / "thumbnail_s.jpg"
    send_telegram(f"ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â± SHORT iniciando\nFrase: {frase}")
    build_audio(tipo, duration, audio_out)
    send_telegram("ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â½ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ Video vertical...")
    build_video_vertical(tipo, duration, video_raw)
    send_telegram("ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚ÂÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â Mezclando AV...")
    merge_av(video_raw, audio_out, video_final)
    send_telegram("ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¼ Metadata + thumbnail...")
    metadata = generate_metadata_short(tipo, frase)
    create_thumbnail_short(tipo, frase, video_raw, thumbnail)
    send_telegram("ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¤ Subiendo Short...")
    video_id = upload_youtube(service, video_final, thumbnail, metadata)
    for f in [audio_out, video_raw, video_final, thumbnail]:
        try: f.unlink()
        except: pass
    return video_id, metadata["titulo"]

def main():
    env_tipo = os.environ.get("VIDEO_TIPO")
    tipo_largo = env_tipo if env_tipo else random.choice(TIPOS)
    tipo_short = env_tipo if env_tipo else random.choice(TIPOS)
    send_telegram(f"FogWindowBeats arrancando\nLARGO: {tipo_largo}\nSHORT: {tipo_short}")
    tmp = BASE / "tmp"
    tmp.mkdir(exist_ok=True)
    service = get_youtube_service()
    try:
        vid_l, titulo_l = pipeline_largo(tipo_largo, service, tmp)
        url_l = f"https://youtu.be/{vid_l}"
        send_telegram(f"LARGO publicado\n{titulo_l}\n{url_l}")
        print(f"LARGO: {url_l}")
    except Exception as e:
        send_telegram(f"Error LARGO: {e}")
        print(f"ERROR LARGO: {e}")
    try:
        vid_s, titulo_s = pipeline_short(tipo_short, service, tmp)
        url_s = f"https://youtube.com/shorts/{vid_s}"
        send_telegram(f"SHORT publicado\n{titulo_s}\n{url_s}")
        print(f"SHORT: {url_s}")
    except Exception as e:
        send_telegram(f"Error SHORT: {e}")
        print(f"ERROR SHORT: {e}")

if __name__ == "__main__":
    main()