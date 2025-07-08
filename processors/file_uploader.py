from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import datetime

def upload_to_drive(file_data: bytes, filename: str) -> str:
    """
    Sube un archivo binario a Google Drive dentro de FACTURAS - IA/MM-YYYY.
    Maneja errores de forma controlada. Devuelve la URL pública del archivo o None.
    """
    # 📁 Nombres de carpetas
    root_folder_name = "FACTURAS - IA"
    month_folder_name = datetime.datetime.now().strftime("%m-%Y")

    try:
        # 🔐 Autenticación
        scopes = ['https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_file('credentials.json', scopes=scopes)
        drive_service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        print(f"❌ Error al autenticar con Google Drive: {e}")
        return None

    # 1️⃣ Buscar o crear carpeta raíz
    try:
        root_query = f"name = '{root_folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
        root_results = drive_service.files().list(q=root_query, spaces='drive', fields='files(id, name)').execute()
        root_folders = root_results.get('files', [])

        if root_folders:
            root_folder_id = root_folders[0]['id']
        else:
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

    # 2️⃣ Buscar o crear subcarpeta MM-YYYY
    try:
        sub_query = (
            f"name = '{month_folder_name}' and mimeType = 'application/vnd.google-apps.folder' "
            f"and '{root_folder_id}' in parents"
        )
        sub_results = drive_service.files().list(q=sub_query, spaces='drive', fields='files(id, name)').execute()
        sub_folders = sub_results.get('files', [])

        if sub_folders:
            folder_id = sub_folders[0]['id']
        else:
            print(f"📁 Creando subcarpeta '{month_folder_name}'...")
            sub_metadata = {
                'name': month_folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [root_folder_id]
            }
            sub_folder = drive_service.files().create(body=sub_metadata, fields='id').execute()
            folder_id = sub_folder['id']
    except Exception as e:
        print(f"❌ Error al obtener o crear la subcarpeta '{month_folder_name}': {e}")
        return None

    # 3️⃣ Subir archivo
    try:
        file_stream = BytesIO(file_data)
        media = MediaIoBaseUpload(file_stream, mimetype='application/pdf', resumable=True)
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
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

    # 4️⃣ Hacer público
    try:
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
    except Exception as e:
        print(f"⚠️ Archivo subido pero no se pudo compartir públicamente: {e}")
        return None  # URL sin `/view`

    return f"https://drive.google.com/file/d/{file_id}/view"
