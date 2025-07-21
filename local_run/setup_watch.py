import os
import time
import json
import pickle
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import sys



# URL dinámica del túnel
if len(sys.argv) < 2:
    print("❌ Debes proporcionar la URL del túnel como argumento.")
    sys.exit(1)

TUNNEL_URL = sys.argv[1].rstrip('/')
PUSH_ENDPOINT = f"{TUNNEL_URL}/gmail-webhook"

# Configuración
PROJECT_ID = 'meta-fulcrum-464615-c5'
SUBSCRIPTION_ID = 'gmail-notificaciones-sub'
TOPIC_NAME = f'projects/{PROJECT_ID}/topics/gmail-notificaciones'
CREDENTIALS_FILE = '../config/credentials_push_notification.json'
TOKEN_PATH = '../config/token.pickle'
WATCH_STATUS_PATH = '../config/watch_status.json'




SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.metadata'
]

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_gmail_service():
    creds = get_credentials()
    return build('gmail', 'v1', credentials=creds)

def save_watch_status(response):
    with open(WATCH_STATUS_PATH, 'w') as f:
        json.dump(response, f, indent=2)
    print(f"✅ Guardado watch_status.json")

def load_watch_status():
    if os.path.exists(WATCH_STATUS_PATH):
        try:
            with open(WATCH_STATUS_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            print("⚠️ No se pudo leer el archivo watch_status.json.")
    return {}

def is_watch_valid():
    watch = load_watch_status()
    expiration = int(watch.get('expiration', 0)) / 1000
    return time.time() < expiration

def create_watch_if_needed():
    if is_watch_valid():
        print("✅ La suscripción 'watch()' sigue vigente.")
        return

    print("🔁 Ejecutando watch() para activar notificaciones...")
    service = get_gmail_service()
    request_body = {
        'labelIds': ['INBOX'],
        'topicName': TOPIC_NAME
    }

    try:
        response = service.users().watch(userId='me', body=request_body).execute()
        print("🔔 Nueva suscripción creada:")
        print(json.dumps(response, indent=2))
        save_watch_status(response)
    except Exception as e:
        print("❌ Error al ejecutar watch():", e)

def create_push_subscription():
    print("⚙️  Verificando suscripción Pub/Sub...")
    try:
        # Borra suscripción si ya existe
        subprocess.run(
            ["gcloud.cmd", "pubsub", "subscriptions", "delete", SUBSCRIPTION_ID, "--quiet"],
            check=False
        )
        

        # Crea suscripción nueva tipo push
        subprocess.run([
            "gcloud.cmd", "pubsub", "subscriptions", "create", SUBSCRIPTION_ID,
            f"--topic=gmail-notificaciones",
            f"--push-endpoint={PUSH_ENDPOINT}",
            "--ack-deadline=10"
        ], check=True)

        print("✅ Suscripción push creada correctamente.")
    except subprocess.CalledProcessError as e:
        print("❌ Error creando la suscripción:", e)

def main():
    create_push_subscription()
    create_watch_if_needed()

if __name__ == '__main__':
    main()