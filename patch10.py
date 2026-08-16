from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = """    canal = "https://www.youtube.com/@FogWindowBeats"
    prompt = f\"\"\"Eres experto en SEO y marketing de YouTube especializado en musica lofi.
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
- descripcion: 500 palabras emotiva, menciona {canal}, timestamps:\\n{timestamps}\\n15+ hashtags al final
- tags: lista de 30 strings SEO incluyendo OBLIGATORIAMENTE: "lofi hip hop radio", "beats to relax study to", "musica para estudiar", "lofi hip hop", "chill beats", "study music 2026", "lofi music", "musica relajante", "concentration music", "focus music", "rain lofi", "lofi beats", "chillhop", "ambient music", "background music"
\"\"\""""

new = """    canal = "https://www.youtube.com/@FogWindowBeats"
    
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
    capitulos_str = "0:00:00 " + caps[0] + "\\n"
    for i, cap in enumerate(caps[1:], 1):
        h = (i * step) // 60
        m = (i * step) % 60
        capitulos_str += f"{h}:{m:02d}:00 {cap}\\n"
    
    prompt = f\"\"\"Eres experto en SEO y marketing de YouTube especializado en musica lofi.
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
- descripcion: texto emotivo 400 palabras, menciona {canal}, incluye estos capitulos al inicio:\\n{capitulos_str}\\nluego los timestamps:\\n{timestamps}\\nTermina con estos 3 hashtags primero (OBLIGATORIO primeros): {top3}\\nluego 15+ hashtags mas
- tags: lista de 30 strings SEO incluyendo OBLIGATORIAMENTE: "lofi hip hop radio", "beats to relax study to", "musica para estudiar", "lofi hip hop", "chill beats", "study music 2026", "lofi music", "musica relajante", "concentration music", "focus music", "rain lofi", "lofi beats", "chillhop", "ambient music", "background music"
\"\"\""""

if old in content:
    content = content.replace(old, new)
    filepath.write_text(content, encoding="utf-8")
    print("Hashtags top3 + capitulos integrados")
else:
    print("ERROR: patron no encontrado")
    idx = content.find("canal = ")
    print(f"Contexto: {repr(content[max(0,idx-20):idx+100])}")