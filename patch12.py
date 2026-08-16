from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = """        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}"""

new = """        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        }"""

old2 = """def upload_youtube(service, video_path, thumbnail_path, metadata):
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
            "selfDeclaredMadeForKids": False,
        }
    }"""

new2 = """def get_next_6am_colombia():
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
    print(f"Programado para: {publish_at}")"""

if old2 in content:
    content = content.replace(old2, new2)
    filepath.write_text(content, encoding="utf-8")
    print("Publicacion programada 6am Colombia integrada")
else:
    print("ERROR: patron no encontrado")
    idx = content.find("def upload_youtube")
    print(f"Contexto: {repr(content[max(0,idx):idx+200])}")