import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import sys

video_id = sys.argv[1]

with open("token.pickle", "rb") as f:
    creds = pickle.load(f)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build("youtube", "v3", credentials=creds)

try:
    service.videos().update(
        part="suggestions",
        body={
            "id": video_id,
            "suggestions": {
                "addScreenElements": [
                    {
                        "type": "subscribeLink",
                        "position": {"type": "corner", "cornerPosition": "topLeft"},
                        "startOffsetMs": 0,
                        "durationMs": 5000
                    }
                ]
            }
        }
    ).execute()
    print(f"Pantalla final agregada a {video_id}")
except Exception as e:
    print(f"Error pantalla final: {e}")