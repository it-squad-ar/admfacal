from mail.gmail_service import GmailService
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from utils.file_utils import get_or_create_folder_path
from io import BytesIO
import datetime
from utils.logger import log_entry

def upload_to_drive(file_data: bytes, filename: str) -> str:
    credentials = GmailService().get_creds()
    if not credentials:
        print("No se pudieron obtener las credenciales de Google Drive.")
        return None

    try:
        drive_service = build('drive', 'v3', credentials=credentials)
        #Add log memory: log_entry(message_id, process_name, level, code, message)
        log_entry(filename, 'upload_to_drive', 'SUCCESS', '0000', 'Success authenticating with Google Drive')
    except Exception as e:
        print(f"Error al autenticar con Google Drive: {e}")
        #Add log memory: log_entry(message_id, process_name, level, code, message)
        log_entry(filename, 'upload_to_drive', 'FATAL', '0001', f'Error al autenticar con Google Drive: {e}')
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
        #Add log memory: log_entry(message_id, process_name, level, code, message)
        log_entry(file_id, 'upload_to_drive', 'SUCCESS', '0000', 'Success uploading document')
    except Exception as e:
        #Add log memory: log_entry(message_id, process_name, level, code, message)
        log_entry(file_id, 'upload_to_drive', 'FATAL', '0001', f"Error al subir el archivo '{filename}': {e}")
        return None

    # 🌍 Compartir
    try:
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        #Add log memory: log_entry(message_id, process_name, level, code, message)
        log_entry(file_id, 'upload_to_drive', 'SUCCESS', '0000', 'Success sharing document')
    except Exception as e:
        #Add log memory: log_entry(message_id, process_name, level, code, message)
        log_entry(file_id, 'upload_to_drive', 'WARNING', '0002', f"Archivo subido pero no se pudo compartir públicamente: {e}")
        return f"https://drive.google.com/file/d/{file_id}"

    return f"https://drive.google.com/file/d/{file_id}/view"
