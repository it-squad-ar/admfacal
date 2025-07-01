from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from base64 import b64encode, urlsafe_b64decode
from email.mime.text import MIMEText

def get_invoice_emails(self):
        print("🔍 Fetching emails...")
        try:
            service = build('gmail', 'v1', credentials=self.get_creds())
            response = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
            messages = response.get('messages', [])

            if not messages:
                print('No emails found.')
                return []
            print(f"Found {len(messages)} emails.")
            emails = []

            for msg in messages:
                msg_id = msg['id']
                email = service.users().messages().get(userId='me', id=msg_id).execute()
                email_body = ''
                if 'payload' in email and 'parts' in email['payload']:
                    for part in email['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            email_body = urlsafe_b64decode(part['body']['data']).decode()
                            break
                emails.append({'id': msg_id, 'body': email_body, 'email': email})
            return emails
        
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

def apply_label(self, messages, label):
    print(f"🏷️ Applying label '{label}' to emails.")
    # Implementación futura

def send_email(self, to_email, subject, body):
    """
    Enviar un correo a `to_email` con el asunto `subject` y cuerpo `body`.
    """
    print(f"✉️ Enviando correo a {to_email}...")

    try:
        service = build('gmail', 'v1', credentials=self.get_creds())
        message = MIMEText(body)
        message['to'] = to_email
        message['from'] = 'me'
        message['subject'] = subject
        raw_message = {'raw': b64encode(message.as_string().encode()).decode()}

        service.users().messages().send(userId='me', body=raw_message).execute()
        print("✅ Correo enviado.")
    except HttpError as error:
        print(f"❌ Error al enviar el correo: {error}")