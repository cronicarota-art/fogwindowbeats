import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

with open("token.pickle", "rb") as f:
    creds = pickle.load(f)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build("youtube", "v3", credentials=creds)

try:
    service.channelBanners().insert(
        media_body=MediaFileUpload("assets/banner.png", mimetype="image/png")
    ).execute()
    print("Banner subido exitosamente")
except Exception as e:
    print(f"Error: {e}")