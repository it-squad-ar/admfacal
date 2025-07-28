from datetime import datetime
from email.mime.text import MIMEText
from base64 import urlsafe_b64encode
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def send_fatal_log_email():
    try:
        # ⬇️ IMPORTACIÓN DIFERIDA
        from mail.gmail_service import GmailService

        service = build('gmail', 'v1', credentials=GmailService().get_creds())
        recipients = ['nacho.frey@gmail.com'] #, 'agustinorc@gmail.com']
        message_text = f'A FATAL error occurred processing invoices. Please check the logs at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.'

        mime_message = MIMEText(message_text)
        mime_message['to'] = ', '.join(recipients)
        mime_message['from'] = 'me'
        mime_message['subject'] = 'Fatal error processing invoices'

        raw_message = {
            'raw': urlsafe_b64encode(mime_message.as_bytes()).decode()
        }

        service.users().messages().send(userId='me', body=raw_message).execute()

    except HttpError as e:
        print(f"❌ Could not send fatal error email: {e}")
