from mail.gmail_service import GmailService
from mail.mail_utils import *
from processors.invoice_parser import process_invoices
from models.llm_interface import extract_invoice_data
#from processors.spreadsheet_updater import update_spreadsheet


def main():
    print("🟢 Starting Invoice Processing...")

    # Conectarse al mail
    messages = get_invoice_emails(GmailService())

    if not messages:
        print("No invoices found.")
        return

    # Procesar facturas
    invoices = process_invoices(messages)
    #print(invoices)
    
    # Obtener datos estructurados
    processed_data = extract_invoice_data(invoices)
    #print(processed_data)

    """
    if invoices:
        update_spreadsheet(invoices)
        gmail.apply_label(messages, "Processed")
    else:
        print("No valid invoices processed.")
    """

    print("✅ Main process Completed.")
    #print(messages)

    #gmail.send_email("agustin.herrera@barbuss.com", "Hola desde Python", "Este es el cuerpo del mensaje.")
    #print("✅ Email sent.")


if __name__ == "__main__":
    main()