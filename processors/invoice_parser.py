import base64
import io
import os
import pytesseract
from googleapiclient.discovery import build
from PIL import Image
from pdf2image import convert_from_bytes
from models.llm_interface import extract_invoice_data

def process_invoices(emails):

    """Procesa una lista de correos con adjuntos y extrae texto con OCR"""
    invoices = []

    for email in emails:
        try:
            print(f"📥 Procesando email {email['id']}")
            message = email['email']
            payload = message.get('payload', {})
            parts = payload.get('parts', [])

            for part in parts:
                filename = part.get('filename')
                body = part.get('body', {})
                attachment_id = body.get('attachmentId')

                if attachment_id and filename:
                    # Adjuntos embebidos (base64 inline)
                    if 'data' in body:
                        file_data = base64.urlsafe_b64decode(body['data'])
                        print(file_data)
                        text = ""

                        if filename.lower().endswith('.pdf'):
                            print("pdf identificado")
                            images = convert_from_bytes(file_data)
                            print()
                            for image in images:
                                text += pytesseract.image_to_string(image)

                        elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
                            print("imagen identificada")
                            image = Image.open(io.BytesIO(file_data))
                            text = pytesseract.image_to_string(image)

                        if text.strip():
                            invoices.append({
                                'id': email['id'],
                                'filename': filename,
                                'text': text.strip()
                            })

                    else:
                        print(f"⚠️ Adjuntos no embebidos en {email['id']}: se requiere el `service` para descargarlos")

        except Exception as e:
            print(f"❌ Error procesando email {email['id']}: {e}")

    return invoices