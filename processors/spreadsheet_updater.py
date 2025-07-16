from mail.gmail_service import GmailService
import gspread
from googleapiclient.discovery import build
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound
from utils.file_utils import get_or_create_folder_path, delete_default_sheet
from utils.logger import log_entry
import datetime

def insert_invoice_data(response_data, spreadsheet_id=None, sheet_name='Facturas Ingresadas'):
    if not response_data:
        print("No hay datos para insertar.")
        return

    try:
        credentials = GmailService().get_creds()
        client = gspread.authorize(credentials)
        drive_service = build('drive', 'v3', credentials=credentials)

        # 📁 Ruta de carpeta: FACTURAS - IA / MM-YYYY
        month_folder = datetime.datetime.now().strftime("%m-%Y")
        folder_path = ["FACTURAS - IA", month_folder]
        parent_folder_id = get_or_create_folder_path(drive_service, folder_path)
        if not parent_folder_id:
            print("No se pudo ubicar o crear la carpeta destino.")
            return

        # 🧾 Crear Spreadsheet si no se proporcionó uno
        if not spreadsheet_id:
            sheet_title = f'Facturas Ingresadas - {month_folder}'
            print("No se proporcionó ID. Creando nuevo spreadsheet.")
            spreadsheet = client.create(sheet_title)
            spreadsheet.share(None, perm_type='anyone', role='writer')
            spreadsheet_id = spreadsheet.id
            print(f"Spreadsheet creado: {spreadsheet_id}")

            # Mover a la carpeta correspondiente
            drive_service.files().update(
                fileId=spreadsheet_id,
                addParents=parent_folder_id,
                removeParents='root',
                fields='id, parents'
            ).execute()
        else:
            try:
                spreadsheet = client.open_by_key(spreadsheet_id)
                #Add log memory: log_entry(message_id, process_name, level, code, message)
                log_entry(response_data["processed_data"], 'insert_invoice_data', 'SUCCESS', '0000', 'Success creating Spreadsheet')
            except SpreadsheetNotFound:
                #Add log memory: log_entry(message_id, process_name, level, code, message)
                log_entry(response_data["processed_data"], 'insert_invoice_data', 'FATAL', '0001', 'Spreadsheet ID not found. Aborting.')
                return

        # 📄 Obtener o crear la hoja
        try:
            sheet = spreadsheet.worksheet(sheet_name)
        except WorksheetNotFound:
            print(f"📄 Pestaña '{sheet_name}' no encontrada. Creando...")
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="10")
            sheet.append_row([
                "message_id", "response_timestamp", "Fecha", "CUITEmisor",
                "RazonSocialEmisor", "PtoVenta", "NroFactura", "Monto",
                "CUITReceptor", "RazonSocialReceptor", "DocURL"
            ])
            delete_default_sheet(spreadsheet)

        # 📥 Insertar datos
        for row in response_data:
            data = row["processed_data"]
            new_row = [
                row["message_id"],
                row["response_timestamp"],
                data.get("Fecha"),
                data.get("CUITEmisor"),
                data.get("RazonSocialEmisor"),
                data.get("PtoVenta"),
                data.get("NroFactura"),
                data.get("Monto"),
                data.get("CUITReceptor"),
                data.get("RazonSocialReceptor"),
                data.get("DocURL")
            ]
            sheet.append_row(new_row, value_input_option='USER_ENTERED')
            #Add log memory: log_entry(message_id, process_name, level, code, message)
            log_entry(row["message_id"], 'insert_invoice_data', 'SUCCESS', '0000', f"Inserted data for message {row['message_id']}")

    except Exception as e:
        #Add log memory: log_entry(message_id, process_name, level, code, message)
        log_entry(row["message_id"], 'insert_invoice_data', 'FATAL', '0001', f"Error inserting data into Sheets: {e}")
