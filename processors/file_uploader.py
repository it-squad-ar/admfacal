from mail.gmail_service import GmailService
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import datetime

def upload_to_drive(file_data: bytes, filename: str) -> str:
    """
    Sube un archivo a Google Drive dentro de:
    FACTURAS - IA / MM-YYYY / Docs.
    Usa credenciales OAuth del usuario. Devuelve la URL pública o None.
    """
    credentials = GmailService().get_creds()

    if not credentials:
        print("❌ No se pudieron obtener las credenciales de Google Drive.")
        return None

    root_folder_name = "FACTURAS - IA"
    month_folder_name = datetime.datetime.now().strftime("%m-%Y")
    docs_folder_name = "Docs"

    try:
        drive_service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        print(f"❌ Error al autenticar con Google Drive: {e}")
        return None

    # 1️⃣ Obtener o crear carpeta raíz FACTURAS - IA
    try:
        root_query = (
            f"name = '{root_folder_name}' "
            f"and mimeType = 'application/vnd.google-apps.folder' "
            f"and trashed = false and 'me' in owners"
        )
        root_results = drive_service.files().list(q=root_query, spaces='drive', fields='files(id, name)').execute()
        root_folders = root_results.get('files', [])
        root_folder_id = root_folders[0]['id'] if root_folders else None

        if not root_folder_id:
            print(f"📁 Creando carpeta raíz '{root_folder_name}'...")
            root_metadata = {
                'name': root_folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            root_folder = drive_service.files().create(body=root_metadata, fields='id').execute()
            root_folder_id = root_folder['id']
    except Exception as e:
        print(f"❌ Error al obtener o crear la carpeta raíz: {e}")
        return None

    # 2️⃣ Obtener o crear subcarpeta MM-YYYY
    try:
        sub_query = (
            f"name = '{month_folder_name}' and mimeType = 'application/vnd.google-apps.folder' "
            f"and '{root_folder_id}' in parents and trashed = false"
        )
        sub_results = drive_service.files().list(q=sub_query, spaces='drive', fields='files(id, name)').execute()
        sub_folders = sub_results.get('files', [])
        month_folder_id = sub_folders[0]['id'] if sub_folders else None

        if not month_folder_id:
            print(f"📁 Creando subcarpeta '{month_folder_name}'...")
            sub_metadata = {
                'name': month_folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [root_folder_id]
            }
            sub_folder = drive_service.files().create(body=sub_metadata, fields='id').execute()
            month_folder_id = sub_folder['id']
    except Exception as e:
        print(f"❌ Error al obtener o crear la subcarpeta '{month_folder_name}': {e}")
        return None

    # 3️⃣ Obtener o crear subcarpeta Docs dentro de MM-YYYY
    try:
        docs_query = (
            f"name = '{docs_folder_name}' and mimeType = 'application/vnd.google-apps.folder' "
            f"and '{month_folder_id}' in parents and trashed = false"
        )
        docs_results = drive_service.files().list(q=docs_query, spaces='drive', fields='files(id, name)').execute()
        docs_folders = docs_results.get('files', [])
        docs_folder_id = docs_folders[0]['id'] if docs_folders else None

        if not docs_folder_id:
            print(f"📁 Creando subcarpeta '{docs_folder_name}' dentro de '{month_folder_name}'...")
            docs_metadata = {
                'name': docs_folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [month_folder_id]
            }
            docs_folder = drive_service.files().create(body=docs_metadata, fields='id').execute()
            docs_folder_id = docs_folder['id']
    except Exception as e:
        print(f"❌ Error al obtener o crear la subcarpeta '{docs_folder_name}': {e}")
        return None

    # 4️⃣ Subir archivo
    try:
        file_stream = BytesIO(file_data)
        media = MediaIoBaseUpload(file_stream, mimetype='application/pdf', resumable=True)
        file_metadata = {
            'name': filename,
            'parents': [docs_folder_id]
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

    # 5️⃣ Compartir archivo (opcional)
    try:
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
    except Exception as e:
        print(f"⚠️ Archivo subido pero no se pudo compartir públicamente: {e}")
        return f"https://drive.google.com/file/d/{file_id}"

    return f"https://drive.google.com/file/d/{file_id}/view"
