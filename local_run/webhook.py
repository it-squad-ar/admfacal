import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify
import base64
import json

import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from mail.gmail_service import GmailService
from mail.mail_utils import *

app = Flask(__name__)

@app.route('/gmail-webhook', methods=['POST'])
def gmail_webhook():
    data = request.get_json()
    print("📬 Webhook recibido:")
    print(json.dumps(data, indent=2))

    if 'message' in data and 'data' in data['message']:
        try:
            decoded = base64.b64decode(data['message']['data']).decode('utf-8')
            print("📨 Contenido del mensaje decodificado:")
            print(decoded)

            parsed = json.loads(decoded)
            history_id = parsed.get("historyId")

            if history_id:
                print(f"🔍 Buscando correos desde historyId: {history_id}")
                messages = get_invoice_emails(GmailService())
                for e in messages:
                    headers = e['email']['payload'].get('headers', [])

                    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(sin asunto)')
                    from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), '(desconocido)')
                    
                    print("📧 From:", from_email)
                    print("📝 Subject:", subject)
                    print("📄 Body:", e['body'])
                    print("-" * 40)
            else:
                print("⚠️ No se encontró historyId en el mensaje.")
        except Exception as e:
            print("❌ Error procesando el mensaje:", e)

    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
