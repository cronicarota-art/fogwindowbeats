import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

with open("token.pickle", "rb") as f:
    creds = pickle.load(f)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build("youtube", "v3", credentials=creds)

CHANNEL_ID = "UCzcgxGQgTS8DbTvswp3OKqw"

secciones = [
    {"title": "Lofi para Estudiar",   "playlist": "PLbwFMyRnG7C0"},
    {"title": "Lluvia + Lofi",         "playlist": "PLCbT9Ko2UMhM"},
    {"title": "Naturaleza Relajante",  "playlist": "PLOh-Zj0_emfg"},
    {"title": "Lofi para Dormir",      "playlist": "PLYDHZ2vnDQTI"},
    {"title": "Jazz Lofi",             "playlist": "PLSuvg6D8DrD0"},
    {"title": "Piano Relajante",       "playlist": "PLYchg6cgQm3k"},
]

for i, sec in enumerate(secciones):
    try:
        service.channelSections().insert(
            part="snippet,contentDetails",
            body={
                "snippet": {
                    "channelId": CHANNEL_ID,
                    "title": sec["title"],
                    "position": i,
                    "type": "singlePlaylist",
                    "style": "verticalList",
                    "defaultLanguage": "es"
                },
                "contentDetails": {
                    "playlists": [sec["playlist"]]
                }
            }
        ).execute()
        print(f"Seccion creada: {sec['title']}")
    except Exception as e:
        print(f"Error {sec['title']}: {e}")