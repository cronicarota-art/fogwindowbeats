import os, random, pickle, subprocess, requests, json, glob, textwrap, re, time, shutil
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
DURACIONES_LARGO = [3600, 5400, 7200]
DURACIONES_SHORT = [40, 45, 50, 60]

PLAYLIST_IDS = {
    "lofi_estudio":    "PLbwFMyRnG7C0",
    "lluvia_lofi":     "PLCbT9Ko2UMhM",
    "jazz_lofi":       "PLSuvg6D8DrD0",
    "naturaleza":      "PLOh-Zj0_emfg",
    "lofi_dormir":     "PLYDHZ2vnDQTI",
    "piano_relajante": "PLYchg6cgQm3k"
}

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
    "el soundtrack de tu mejor dia",
    "POV estas en modo productividad",
    "cuando el cafe ya no es suficiente",
    "esto es lo que necesitas ahora",
    "modo biblioteca activado",
    "tu cerebro en modo zen"
]

COMENTARIOS_LARGO = [
    "Guardalo para tu proxima sesion de estudio! FogWindowBeats",
    "Ponlo en bucle y desaparece del mundo. Suscribete para mas lofi!",
    "El soundtrack perfecto para ser productivo hoy. FogWindowBeats",
    "Comparte con alguien que necesite concentrarse ahora mismo!",
    "Suscribete para mas lofi todos los dias. FogWindowBeats"
]

COMENTARIOS_SHORT = [
    "Guardalo para tu proxima sesion de estudio!",
    "Ponlo en bucle y a trabajar!",
    "El soundtrack perfecto para hoy",
    "Siguenos para mas lofi todos los dias!",
    "Comparte con alguien que necesite concentrarse",
    "Suscribete para mas vibes lofi"
]

ETIQUETAS = {
    "lofi_estudio":    "lofi para estudiar",
    "lluvia_lofi":     "lluvia + lofi",
    "jazz_lofi":       "jazz lofi",
    "naturaleza":      "naturaleza relajante",
    "lofi_dormir":     "lofi para dormir",
    "piano_relajante": "piano relajante"
}

COLORES_TIPO = {
    "lofi_estudio":    [(20,20,60), (80,40,180), (40,180,220)],
    "lluvia_lofi":     [(10,20,50), (30,80,180), (80,200,255)],
    "jazz_lofi":       [(40,15,10), (180,80,20), (220,160,40)],
    "naturaleza":      [(10,30,15), (20,120,50), (80,220,100)],
    "lofi_dormir":     [(15,10,40), (60,20,120), (140,60,200)],
    "piano_relajante": [(30,10,40), (140,40,160), (220,100,240)]
}

WATERMARK_H = "drawtext=text=FogWindowBeats:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=38:fontcolor=white@0.65:x=(w-text_w)/2:y=25:shadowcolor=black@0.6:shadowx=2:shadowy=2"
WATERMARK_V = "drawtext=text=FogWindowBeats:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=46:fontcolor=white@0.65:x=(w-text_w)/2:y=25:shadowcolor=black@0.6:shadowx=2:shadowy=2"

COLOR_GRADE = {
    "lofi_estudio":    "colortemperature=temperature=4500",
    "lluvia_lofi":     "colorbalance=bs=0.1:bm=0.05:bh=0.05",
    "jazz_lofi":       "colortemperature=temperature=3800",
    "naturaleza":      "colorbalance=gs=0.05:gm=0.05:gh=0.05",
    "lofi_dormir":     "colorbalance=bs=0.08:bm=0.05:bh=0.05",
    "piano_relajante": "colortemperature=temperature=4200"
}

def clean_text(text):
    return text.encode("ascii", "ignore").decode("ascii")

def clean_for_telegram(text):
    return re.sub(r"[^\x00-\x7F]+", "", str(text)).strip()

def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": clean_for_telegram(msg), "parse_mode": "HTML"},
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
    return glob.glob(str(ASSETS / folder / "*.mp4"))

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

def write_concat(files, path):
    with open(path, "w", encoding="utf-8") as f:
        for vf in files:
            f.write(f"file '{vf}'\n")

def build_audio(tipo, duration, output_path):
    audio_files = get_audio_files(tipo)
    if not audio_files:
        raise Exception(f"No hay audios para {tipo}")
    random.shuffle(audio_files)
    concat_list = BASE / "audio_concat.txt"
    write_concat(audio_files, concat_list)
    run_ffmpeg([
        "ffmpeg", "-y", "-stream_loop", "-1",
        "-f", "concat", "-safe", "0",
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
    write_concat(video_files, concat_list)
    grade = COLOR_GRADE.get(tipo, "")
    vf_h = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1"
    if grade:
        vf_h += f",{grade}"
    vf_h += ",fps=24,format=yuv420p"
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

def build_video_vertical(tipo, duration, output_path, frase=''):
    video_files = get_video_files_vertical()
    if not video_files:
        video_files = get_video_files(tipo)
    if not video_files:
        raise Exception("No hay videos verticales")
    random.shuffle(video_files)
    concat_list = BASE / "video_concat_v.txt"
    write_concat(video_files, concat_list)
    words = frase.encode("ascii","ignore").decode().split()
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
    concat_list.unlink(missing_ok=True)

def merge_av(video_path, audio_path, output_path, vertical=False):
    wm = WATERMARK_V if vertical else WATERMARK_H
    vf = wm
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30",
        "-c:a", "copy",
        "-shortest", str(output_path)
    ])

def add_intro(video_path, output_path):
    intro = ASSETS / "intro.mp4"
    if not intro.exists():
        shutil.copy(str(video_path), str(output_path))
        return
    concat_list = BASE / "intro_concat.txt"
    write_concat([str(intro), str(video_path)], concat_list)
    run_ffmpeg([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy", str(output_path)
    ])
    concat_list.unlink(missing_ok=True)

def extract_frame(video_path, output_path, width, height):
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-ss", "00:00:03",
        "-vframes", "1",
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
        str(output_path)
    ])

AB_STYLE = ["cinematic", "minimal"]

def create_thumbnail_largo(tipo, titulo, duration_h, video_path, output_path, style=None):
    if style is None:
        import random
        style = random.choice(AB_STYLE)
    print(f"Thumbnail style: {style}")
    frame_path = output_path.parent / "frame_tmp.jpg"
    try:
        extract_frame(video_path, frame_path, 1280, 720)
        img = Image.open(str(frame_path)).convert("RGB").resize((1280, 720))
    except:
        img = Image.new("RGB", (1280, 720), color=(10, 8, 25))
    overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 140))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        font_big = ImageFont.load_default()
        font_med = font_big
        font_small = font_big
    draw.ellipse([(30, 25), (145, 140)], fill=(255, 200, 0))
    draw.text((87, 82), f"{duration_h}H", font=font_med, fill=(20, 10, 50), anchor="mm")
    titulo_clean = clean_text(titulo)
    lines = textwrap.wrap(titulo_clean, width=22)
    y = 230
    for line in lines[:3]:
        draw.text((640, y), line, font=font_big, fill=(255, 255, 255), anchor="mm",
                  stroke_width=3, stroke_fill=(0, 0, 0))
        y += 90
    draw.rectangle([(0, 630), (1280, 720)], fill=(0, 0, 0))
    draw.text((640, 675), ETIQUETAS.get(tipo, "lofi beats"), font=font_med,
              fill=(200, 220, 255), anchor="mm")
    draw.text((1240, 710), "FogWindowBeats", font=font_small,
              fill=(150, 150, 200), anchor="rm")
    img.save(str(output_path), "JPEG", quality=95)
    if frame_path.exists():
        frame_path.unlink()

def create_thumbnail_short(tipo, frase, video_path, output_path):
    frame_path = output_path.parent / "frame_s_tmp.jpg"
    bg, c1, c2 = COLORES_TIPO.get(tipo, [(10,8,25),(80,40,180),(40,180,220)])
    try:
        extract_frame(video_path, frame_path, 1080, 1920)
        img = Image.open(str(frame_path)).convert("RGB").resize((1080, 1920))
    except:
        img = Image.new("RGB", (1080, 1920), color=bg)
    overlay_img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 110))
    img = Image.alpha_composite(img.convert("RGBA"), overlay_img).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.ellipse([(-100,600),(500,1200)], fill=(*c1,60))
    draw.ellipse([(600,900),(1200,1500)], fill=(*c2,50))
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
    except:
        font_big = ImageFont.load_default()
        font_med = font_big
        font_small = font_big
    frase_clean = clean_text(frase)
    lines = textwrap.wrap(frase_clean, width=15)
    total_h = len(lines) * 110
    y = (1920 - total_h) // 2 - 50
    pad = 30
    draw.rectangle([(40, y-pad), (1040, y+total_h+pad)], fill=(0,0,0,180))
    for line in lines:
        draw.text((540, y), line, font=font_big, fill=(255,255,255), anchor="mm",
                  stroke_width=4, stroke_fill=(0,0,0))
        y += 110
    draw.rectangle([(0,0),(1080,90)], fill=(0,0,0,160))
    draw.text((540,45), "FogWindowBeats", font=font_med, fill=(200,210,255), anchor="mm")
    draw.rectangle([(0,1830),(1080,1920)], fill=(0,0,0,160))
    draw.text((540,1875), "Suscribete para mas lofi", font=font_small, fill=(200,200,255), anchor="mm")
    img.save(str(output_path), "JPEG", quality=95)
    if frame_path.exists():
        frame_path.unlink()

def generate_metadata_largo(tipo, duration_h):
    client = Groq(api_key=GROQ_API_KEY)
    timestamps = ""
    mins = int(duration_h * 60)
    for i in range(0, min(mins, 480), 30):
        h = i // 60
        m = i % 60
        timestamps += f"{h:02d}:{m:02d}:00 - Lofi Mix\n"
    canal = "https://www.youtube.com/@FogWindowBeats"
    
    HASHTAGS_TOP3 = {
        "lofi_estudio":    "#lofi #musicapararelajarse #estudiar",
        "lluvia_lofi":     "#lluvia #lofi #rainlofi",
        "jazz_lofi":       "#jazzlofi #lofi #chillbeats",
        "naturaleza":      "#naturaleza #lofi #relajacion",
        "lofi_dormir":     "#lofi #dormir #relajacion",
        "piano_relajante": "#piano #lofi #musicarelajante"
    }
    top3 = HASHTAGS_TOP3.get(tipo, "#lofi #musicapararelajarse #estudiar")
    
    CAPITULOS = {
        "lofi_estudio":    ["Warm Up Session", "Deep Focus Mode", "Coffee Break Beats", "Late Night Study", "Final Push"],
        "lluvia_lofi":     ["Primera Lluvia", "Tormenta Perfecta", "Ventana Lluviosa", "Lluvia Profunda", "Calma Total"],
        "jazz_lofi":       ["Jazz Intro", "Midnight Cafe", "Smooth Groove", "Late Night Jazz", "Jazz Finale"],
        "naturaleza":      ["Amanecer", "Bosque Profundo", "Rio Tranquilo", "Tarde en el Campo", "Atardecer"],
        "lofi_dormir":     ["Relajacion Inicial", "Mente en Calma", "Sueno Profundo", "Paz Total", "Descanso Pleno"],
        "piano_relajante": ["Piano Suave", "Melodia Principal", "Variacion Lirica", "Crescendo", "Final en Calma"]
    }
    caps = CAPITULOS.get(tipo, ["Intro", "Parte 1", "Parte 2", "Parte 3", "Finale"])
    mins_total = int(duration_h * 60)
    step = mins_total // len(caps)
    capitulos_str = "0:00:00 " + caps[0] + "\n"
    for i, cap in enumerate(caps[1:], 1):
        h = (i * step) // 60
        m = (i * step) % 60
        capitulos_str += f"{h}:{m:02d}:00 {cap}\n"
    
    prompt = f"""Eres experto en SEO y marketing de YouTube especializado en musica lofi.
Genera metadata VIRAL para video tipo "{tipo}".

REGLAS TITULO:
- Maximo 80 caracteres
- Mezcla espanol e ingles naturalmente, ejemplo: "Lluvia Lofi para Estudiar - Rain Beats to Focus"
- NO incluyas la duracion en el titulo
- Enfocate en EMOCION y BENEFICIO
- Estilo: "Rain Lofi para Concentrarte sin Parar", "Study Beats - Lofi para Trabajar sin Distracciones"
- NUNCA: "Musica Lofi 3.0 horas", "Lofi Mix"

TIPO: {tipo}
EMOCIONES: lofi_estudio=concentracion cafe madrugada productividad, lluvia_lofi=lluvia cozy noche tormenta, jazz_lofi=elegancia cafe nocturno smooth, naturaleza=paz bosque aire fresco, lofi_dormir=relajacion profunda calma, piano_relajante=belleza emocion alma

JSON con exactamente estas claves:
- titulo: string viral bilingue
- descripcion: texto emotivo 400 palabras, menciona {canal}, incluye estos capitulos al inicio:\n{capitulos_str}\nluego los timestamps:\n{timestamps}\nTermina con estos 3 hashtags primero (OBLIGATORIO primeros): {top3}\nluego 15+ hashtags mas
- tags: lista de 30 strings SEO incluyendo OBLIGATORIAMENTE: "lofi hip hop radio", "beats to relax study to", "musica para estudiar", "lofi hip hop", "chill beats", "study music 2026", "lofi music", "musica relajante", "concentration music", "focus music", "rain lofi", "lofi beats", "chillhop", "ambient music", "background music"
"""
    r = client.chat.completions.create(
        model="qwen/qwen3-27b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=2000
    )
    return json.loads(r.choices[0].message.content, strict=False)

def generate_metadata_short(tipo, frase):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""Eres experto en YouTube Shorts virales de lofi.
Genera metadata para Short tipo "{tipo}", frase: "{frase}"

REGLAS TITULO:
- Maximo 60 chars
- DEBE tener 2-3 emojis relevantes
- Estilo casual minusculas con emojis
- Ejemplos: "pov: son las 3am y tienes que entregar", "modo biblioteca activado"
- NUNCA sin emojis

JSON con exactamente estas claves:
- titulo: string viral casual con emojis
- descripcion: 3 lineas emotivas + hashtags #lofi #shorts #estudiar #concentracion #fyp #parati #musicalofi #lofihiphop #chillbeats #studymusic
- tags: lista de 15 tags cortos lofi shorts viral
"""
    r = client.chat.completions.create(
        model="qwen/qwen3-27b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=600
    )
    return json.loads(r.choices[0].message.content, strict=False)

def add_to_playlist(service, video_id, tipo):
    playlist_id = PLAYLIST_IDS.get(tipo)
    if not playlist_id:
        return
    try:
        service.playlistItems().insert(
            part="snippet",
            body={"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}}
        ).execute()
        print(f"Agregado a playlist {tipo}")
    except Exception as e:
        print(f"Error playlist: {e}")

def post_comment(service, video_id, comment_text):
    try:
        service.commentThreads().insert(
            part="snippet",
            body={"snippet": {"videoId": video_id, "topLevelComment": {"snippet": {"textOriginal": comment_text}}}}
        ).execute()
        print("Comentario publicado")
    except Exception as e:
        print(f"Error comentario: {e}")

def post_community(service, text):
    try:
        service.communityPosts().insert(
            part="snippet",
            body={"snippet": {"textOriginal": text}}
        ).execute()
        print("Post de comunidad publicado")
    except Exception as e:
        print(f"Error comunidad: {e}")

def auto_reply_comments(service, video_id):
    RESPUESTAS = [
        "Gracias por escuchar! Suscribete para mas lofi todos los dias",
        "Nos alegra que lo disfrutes! Activa la campana para no perderte nada",
        "Que bueno tenerte aqui! Comparte con alguien que necesite concentrarse",
        "Gracias! Hay mas contenido lofi en el canal para ti",
        "Bienvenido a FogWindowBeats! Suscribete para mas vibes lofi"
    ]
    import random, time
    try:
        time.sleep(30)
        comments = service.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=10,
            order="time"
        ).execute()
        for item in comments.get("items", []):
            comment_id = item["id"]
            try:
                service.comments().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "parentId": comment_id,
                            "textOriginal": random.choice(RESPUESTAS)
                        }
                    }
                ).execute()
                print(f"Respuesta enviada a {comment_id}")
                time.sleep(2)
            except Exception as e:
                print(f"Error respuesta: {e}")
    except Exception as e:
        print(f"Error auto_reply: {e}")

def get_next_6am_colombia():
    from datetime import datetime, timezone, timedelta
    colombia = timezone(timedelta(hours=-5))
    now = datetime.now(colombia)
    target = now.replace(hour=6, minute=0, second=0, microsecond=0)
    if now.hour >= 6:
        target += timedelta(days=1)
    return target.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

def upload_youtube(service, video_path, thumbnail_path, metadata):
    publish_at = get_next_6am_colombia()
    body = {
        "snippet": {
            "title": metadata["titulo"],
            "description": metadata["descripcion"],
            "tags": metadata["tags"],
            "categoryId": "10",
            "defaultLanguage": "es"
        },
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False,
            "publishAt": publish_at
        }
    }
    print(f"Programado para: {publish_at}")
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True, chunksize=1024*1024*5)
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
    video_with_intro = tmp / "video_intro.mp4"
    video_final = tmp / "video_final.mp4"
    thumbnail = tmp / "thumbnail.jpg"
    send_telegram(f"<b>LARGO</b> | {tipo} | {duration_h}h")
    build_audio(tipo, duration, audio_out)
    send_telegram("Construyendo video...")
    build_video_horizontal(tipo, duration, video_raw)
    send_telegram("Agregando intro...")
    add_intro(video_raw, video_with_intro)
    send_telegram("Mezclando AV + watermark + overlay...")
    merge_av(video_with_intro, audio_out, video_final, vertical=False)
    send_telegram("Metadata + thumbnail...")
    metadata = generate_metadata_largo(tipo, duration_h)
    create_thumbnail_largo(tipo, metadata["titulo"], duration_h, video_raw, thumbnail)
    send_telegram("Subiendo a YouTube...")
    video_id = upload_youtube(service, video_final, thumbnail, metadata)
    add_to_playlist(service, video_id, tipo)
    time.sleep(5)
    post_comment(service, video_id, random.choice(COMENTARIOS_LARGO))
    try:
        end_ms = duration * 1000
        start_ms = max(0, end_ms - 20000)
        service.videos().update(
            part="suggestions",
            body={
                "id": video_id,
                "suggestions": {
                    "addScreenElements": [
                        {
                            "type": "subscribeLink",
                            "position": {"type": "corner", "cornerPosition": "topLeft"},
                            "startOffsetMs": start_ms,
                            "durationMs": 20000
                        }
                    ]
                }
            }
        ).execute()
        print("Pantalla final agregada")
    except Exception as e:
        print(f"Error pantalla final: {e}")
    try:
        titulo_community = metadata.get("titulo", "nuevo lofi")
        community_text = f"Nuevo video disponible! {titulo_community} - Escuchalo ahora en FogWindowBeats. Link en el canal. #lofi #estudiar #concentracion"
        post_community(service, community_text[:500])
    except Exception as e:
        print(f"Error comunidad: {e}")
    auto_reply_comments(service, video_id)
    for f in [audio_out, video_raw, video_with_intro, video_final, thumbnail]:
        try: f.unlink()
        except: pass
    return video_id, metadata["titulo"]

def pipeline_short(tipo, service, tmp):
    duration = random.choice(DURACIONES_SHORT)
    frase = random.choice(FRASES_SHORT)
    print(f"SHORT | tipo={tipo} | {duration}s")
    audio_out = tmp / "audio_s.aac"
    video_raw = tmp / "video_raw_s.mp4"
    video_final = tmp / "video_final_s.mp4"
    thumbnail = tmp / "thumbnail_s.jpg"
    send_telegram(f"<b>SHORT</b> | {tipo} | {duration}s")
    build_audio(tipo, duration, audio_out)
    send_telegram("Video vertical...")
    build_video_vertical(tipo, duration, video_raw, frase=frase)
    send_telegram("Mezclando AV + watermark...")
    merge_av(video_raw, audio_out, video_final, vertical=True)
    send_telegram("Metadata + thumbnail...")
    metadata = generate_metadata_short(tipo, frase)
    create_thumbnail_short(tipo, frase, video_raw, thumbnail)
    send_telegram("Subiendo Short...")
    video_id = upload_youtube(service, video_final, thumbnail, metadata)
    add_to_playlist(service, video_id, tipo)
    time.sleep(5)
    post_comment(service, video_id, random.choice(COMENTARIOS_SHORT))
    auto_reply_comments(service, video_id)
    for f in [audio_out, video_raw, video_final, thumbnail]:
        try: f.unlink()
        except: pass
    return video_id, metadata["titulo"]

def get_best_publish_time(service):
    try:
        from datetime import datetime, timezone
        report = service.reports().query(
            ids="channel==MINE",
            startDate="2026-01-01",
            endDate="2026-12-31",
            metrics="views",
            dimensions="day",
            sort="-views",
            maxResults=7
        ).execute()
        print(f"Analytics consultado: {report}")
    except Exception as e:
        print(f"Analytics no disponible: {e}")
    return None

def main():
    env_tipo = os.environ.get("VIDEO_TIPO")
    tipo_largo = env_tipo if env_tipo else random.choice(TIPOS)
    tipo_short = env_tipo if env_tipo else random.choice(TIPOS)
    send_telegram(f"<b>FogWindowBeats</b> iniciando\n<b>Largo:</b> {tipo_largo}\n<b>Short:</b> {tipo_short}")
    tmp = BASE / "tmp"
    tmp.mkdir(exist_ok=True)
    service = get_youtube_service()
    try:
        vid_l, titulo_l = pipeline_largo(tipo_largo, service, tmp)
        url_l = f"https://youtu.be/{vid_l}"
        send_telegram(f"<b>LARGO publicado</b>\n{url_l}")
        print(f"LARGO: {url_l}")
    except Exception as e:
        send_telegram(f"<b>Error LARGO:</b> {clean_for_telegram(str(e))}")
        print(f"ERROR LARGO: {e}")
    try:
        vid_s, titulo_s = pipeline_short(tipo_short, service, tmp)
        url_s = f"https://youtube.com/shorts/{vid_s}"
        send_telegram(f"<b>SHORT publicado</b>\n{url_s}")
        print(f"SHORT: {url_s}")
    except Exception as e:
        send_telegram(f"<b>Error SHORT:</b> {clean_for_telegram(str(e))}")
        print(f"ERROR SHORT: {e}")

if __name__ == "__main__":
    main()