from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old = """def post_community(service, text):
    try:
        service.communityPosts().insert(
            part="snippet",
            body={"snippet": {"textOriginal": text}}
        ).execute()
        print("Post de comunidad publicado")
    except Exception as e:
        print(f"Error comunidad: {e}")"""

new = """def post_community(service, text):
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
        print(f"Error auto_reply: {e}")"""

if old in content:
    content = content.replace(old, new)
    filepath.write_text(content, encoding="utf-8")
    print("auto_reply_comments agregado")
else:
    print("ERROR: patron no encontrado")