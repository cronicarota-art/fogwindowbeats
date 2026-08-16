import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

with open("token.pickle", "rb") as f:
    creds = pickle.load(f)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build("youtube", "v3", credentials=creds)

service.channels().update(
    part="brandingSettings",
    body={
        "id": "UCzcgxGQgTS8DbTvswp3OKqw",
        "brandingSettings": {
            "channel": {
                "description": "FogWindowBeats - Tu espacio de lofi 24/7\n\nMusica lofi con lluvia, naturaleza y jazz para estudiar, concentrarte, trabajar y relajarte.\n\nNuevos videos todos los dias.\n\nSuscribete y activa la campana para no perderte nada.\n\n#lofi #musicapararelajarse #estudiar #concentracion #lofihiphop",
                "keywords": "lofi musica para estudiar concentracion lluvia lofi hip hop chill beats study music focus music lofi beats",
                "country": "CO"
            }
        }
    }
).execute()
print("Canal actualizado")