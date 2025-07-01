from mail.gmail_service import GmailService
from processors.invoice_parser import process_invoices
from processors.spreadsheet_updater import update_spreadsheet


def main():
    print("🟢 Starting Invoice Processing...")

    # Conectarse al mail
    gmail = GmailService()
    messages = gmail.get_invoice_emails()

    if not messages:
        print("No invoices found.")
        return

    # Procesar facturas
    invoices = process_invoices(messages)

    if invoices:
        update_spreadsheet(invoices)
        gmail.apply_label(messages, "Processed")
    else:
        print("No valid invoices processed.")

    print("✅ Process Completed.")


if __name__ == "__main__":
    main()