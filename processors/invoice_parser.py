from models.llm_interface import extract_invoice_data


def process_invoices(messages):
    invoices = []

    for msg in messages:
        print(f"📥 Processing message {msg.get('id')}")

        data = extract_invoice_data(msg)

        if data:
            invoices.append(data)
        else:
            print(f"⚠️ Failed to process {msg.get('id')}")

    return invoices
