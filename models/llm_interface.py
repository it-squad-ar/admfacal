def extract_invoice_data(message):
    """
    Extraer datos de la factura desde el cuerpo del correo
    o sus adjuntos, usando LLM o parsing.
    """
    print(f"🤖 Extracting invoice data from message {message.get('id')}")

    # TODO: Implementar llamada a LLM y parseo
    # Simulamos datos
    return {
        "Fecha": "2024-07-01",
        "CUIT": "30-12345678-9",
        "NroFactura": "A-0001-123456",
        "Monto": 12345.67,
        "RazonSocial": "Empresa Ejemplo SRL"
    }
