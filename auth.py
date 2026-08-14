import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

flow = InstalledAppFlow.from_client_secrets_file("scripts/client_secrets.json", SCOPES)
credentials = flow.run_local_server(port=0)

with open("token.pickle", "wb") as f:
    pickle.dump(credentials, f)

print("✅ Token guardado en token.pickle")