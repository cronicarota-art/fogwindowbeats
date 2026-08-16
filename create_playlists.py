import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

with open("token.pickle", "rb") as f:
    creds = pickle.load(f)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build("youtube", "v3", credentials=creds)

playlists = [
    ("lofi_estudio",    "Lofi para Estudiar - FogWindowBeats"),
    ("lluvia_lofi",     "Lluvia + Lofi - FogWindowBeats"),
    ("jazz_lofi",       "Jazz Lofi - FogWindowBeats"),
    ("naturaleza",      "Naturaleza Relajante - FogWindowBeats"),
    ("lofi_dormir",     "Lofi para Dormir - FogWindowBeats"),
    ("piano_relajante", "Piano Relajante - FogWindowBeats"),
]

playlist_ids = {}
for tipo, titulo in playlists:
    r = service.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": titulo,
                "description": f"La mejor musica lofi de FogWindowBeats. Suscribete para mas contenido todos los dias."
            },
            "status": {"privacyStatus": "public"}
        }
    ).execute()
    playlist_ids[tipo] = r["id"]
    print(f"{tipo}: {r['id']}")

with open("playlist_ids.txt", "w") as f:
    for k, v in playlist_ids.items():
        f.write(f"{k}={v}\n")

print("Playlists creadas!")