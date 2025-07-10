import base64
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from base64 import b64encode, urlsafe_b64decode
from email.mime.text import MIMEText

def get_invoice_emails(self):
    print("🔍 Fetching emails...")
    try:
        service = build('gmail', 'v1', credentials=self.get_creds())
        # Utilizar q como filtro de busqueda
        response = service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                q='is:unread',
                maxResults=10
            ).execute()

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
            attachments = []

            payload = email.get('payload', {})
            parts = payload.get('parts', [])

            for part in parts:
                mime_type = part.get('mimeType')
                filename = part.get('filename')
                body = part.get('body', {})
                data = body.get('data')
                attachment_id = body.get('attachmentId')

                # Obtener cuerpo de texto
                if mime_type == 'text/plain' and data:
                    email_body = base64.urlsafe_b64decode(data).decode()

                # Procesar adjuntos
                if filename and attachment_id:
                    if data:
                        file_data = base64.urlsafe_b64decode(data)
                    else:
                        attachment = service.users().messages().attachments().get(
                            userId='me',
                            messageId=msg_id,
                            id=attachment_id
                        ).execute()
                        file_data = base64.urlsafe_b64decode(attachment['data'])

                    attachments.append({
                        'filename': filename,
                        'data': file_data
                    })

            emails.append({
                'id': msg_id,
                'body': email_body,
                'email': email,
                'attachments': attachments
            })

        return emails

    except HttpError as error:
        print(f'❌ An error occurred: {error}')
        return []

def apply_label(self, messages, label):
    print(f"🏷️ Applying label '{label}' to emails.")
    # TODO: Aplicar etiqueta a los emails de FACTURAS - IA. Si la etiqueta no existe, entonces crearla.

def mark_read(self, messages, label):
    print(f"🏷️ Setting mails to read state")
    # TODO: Marcar como leido los correos que se procesaron.

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