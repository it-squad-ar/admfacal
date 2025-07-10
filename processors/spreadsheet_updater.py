from mail.gmail_service import GmailService
import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound

def insert_invoice_data(response_data, spreadsheet_id=None, sheet_name="IA Facturas"):
    """
    Inserta datos de facturas en Google Sheets. Crea la hoja si no existe.
    Parámetros:
    - response_data: salida de extract_invoice_data (lista de dicts)
    - spreadsheet_id: ID del Google Sheet (str)
    - sheet_name: nombre de la pestaña (str)
    """

    if not response_data:
        print("⚠️ No hay datos para insertar.")
        return

    try:
        # Autenticación
        credentials = GmailService().get_creds()
        client = gspread.authorize(credentials)

        # Obtener o crear el spreadsheet
        if spreadsheet_id:
            try:
                spreadsheet = client.open_by_key(spreadsheet_id)
            except SpreadsheetNotFound:
                print("❌ Spreadsheet ID no encontrado. Abortando.")
                return
        else:
            print("⚠️ No se proporcionó ID. Creando nuevo spreadsheet.")
            spreadsheet = client.create("Facturas Ingresadas")
            spreadsheet.share(None, perm_type='anyone', role='writer')  # Opcional: acceso público para edición
            spreadsheet_id = spreadsheet.id
            print(f"🆕 Spreadsheet creado: {spreadsheet_id}")

        # Obtener o crear la worksheet
        try:
            sheet = spreadsheet.worksheet(sheet_name)
        except WorksheetNotFound:
            print(f"📄 Pestaña '{sheet_name}' no encontrada. Creando...")
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="10")
            # Agregar encabezados
            sheet.append_row(["message_id", "response_timestamp", "Fecha", "CUIT", "NroFactura", "Monto", "RazonSocial"])

        # Insertar datos
        for row in response_data:
            data = row["processed_data"]
            new_row = [
                row["message_id"],
                row["response_timestamp"],
                data.get("Fecha"),
                data.get("CUIT"),
                data.get("NroFactura"),
                data.get("Monto"),
                data.get("RazonSocial")
            ]
            sheet.append_row(new_row, value_input_option='USER_ENTERED')
            print(f"✅ Inserted data for message {row['message_id']}")

    except Exception as e:
        print(f"❌ Error inserting data into Sheets: {e}")
