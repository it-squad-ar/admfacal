from mail.gmail_service import GmailService
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from utils.file_utils import get_or_create_folder_path
from io import BytesIO
import datetime

def upload_to_drive(file_data: bytes, filename: str) -> str:
    credentials = GmailService().get_creds()
    if not credentials:
        print("❌ No se pudieron obtener las credenciales de Google Drive.")
        return None

    try:
        drive_service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        print(f"❌ Error al autenticar con Google Drive: {e}")
        return None

    # 📁 Ruta de carpetas: FACTURAS - IA / MM-YYYY / Docs
    month_folder = datetime.datetime.now().strftime("%m-%Y")
    folder_path = ["FACTURAS - IA", month_folder, "Docs"]
    parent_folder_id = get_or_create_folder_path(drive_service, folder_path)
    if not parent_folder_id:
        return None

    # 📤 Subir archivo
    try:
        file_stream = BytesIO(file_data)
        media = MediaIoBaseUpload(file_stream, mimetype='application/pdf', resumable=True)
        file_metadata = {
            'name': filename,
            'parents': [parent_folder_id]
        }
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        file_id = uploaded_file['id']
    except Exception as e:
        print(f"❌ Error al subir el archivo '{filename}': {e}")
        return None

    # 🌍 Compartir
    try:
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
    except Exception as e:
        print(f"⚠️ Archivo subido pero no se pudo compartir públicamente: {e}")
        return f"https://drive.google.com/file/d/{file_id}"

    return f"https://drive.google.com/file/d/{file_id}/view"
