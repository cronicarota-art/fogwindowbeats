from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = """def main():
    env_tipo = os.environ.get("VIDEO_TIPO")
    tipo_largo = env_tipo if env_tipo else random.choice(TIPOS)
    tipo_short = env_tipo if env_tipo else random.choice(TIPOS)"""

new = """def get_best_publish_time(service):
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
    tipo_short = env_tipo if env_tipo else random.choice(TIPOS)"""

if old in content:
    content = content.replace(old, new)
    filepath.write_text(content, encoding="utf-8")
    print("Horario inteligente agregado")
else:
    print("ERROR: patron no encontrado")