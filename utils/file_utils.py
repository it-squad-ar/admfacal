from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_or_create_folder_path(drive_service, folder_names: list[str]) -> str:
    """
    Crea o retorna el ID de una ruta de carpetas anidadas en Drive.
    - folder_names: lista de nombres de carpetas desde la raíz (My Drive).
    """
    parent_id = None

    for folder_name in folder_names:
        query = (
            f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' "
            f"and trashed = false"
        )
        if parent_id:
            query += f" and '{parent_id}' in parents"
        else:
            query += f" and 'me' in owners"

        try:
            results = drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()

            folders = results.get('files', [])
            if folders:
                parent_id = folders[0]['id']
            else:
                metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                }
                if parent_id:
                    metadata['parents'] = [parent_id]

                folder = drive_service.files().create(body=metadata, fields='id').execute()
                parent_id = folder['id']

        except HttpError as e:
            print(f"❌ Error al crear/obtener la carpeta '{folder_name}': {e}")
            return None

    return parent_id
