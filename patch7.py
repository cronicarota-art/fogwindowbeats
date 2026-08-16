from pathlib import Path

filepath = Path("C:/LofiZen/scripts/pipeline.py")
content = filepath.read_text(encoding="utf-8")

old1 = """    except Exception as e:
        print(f"Error comunidad: {e}")
    for f in [audio_out, video_raw, video_with_intro, video_final, thumbnail]:"""

new1 = """    except Exception as e:
        print(f"Error comunidad: {e}")
    auto_reply_comments(service, video_id)
    for f in [audio_out, video_raw, video_with_intro, video_final, thumbnail]:"""

old2 = """    post_comment(service, video_id, random.choice(COMENTARIOS_SHORT))
    for f in [audio_out, video_raw, video_final, thumbnail]:"""

new2 = """    post_comment(service, video_id, random.choice(COMENTARIOS_SHORT))
    auto_reply_comments(service, video_id)
    for f in [audio_out, video_raw, video_final, thumbnail]:"""

if old1 in content:
    content = content.replace(old1, new1)
    print("auto_reply en largo OK")
else:
    print("ERROR: patron largo no encontrado")

if old2 in content:
    content = content.replace(old2, new2)
    print("auto_reply en short OK")
else:
    print("ERROR: patron short no encontrado")

filepath.write_text(content, encoding="utf-8")