import requests
import json
from datetime import datetime
from processors.spreadsheet_updater import insert_invoice_data

def extract_invoice_data(messages):
    """
    Extrae datos de facturas desde el campo 'text' de una lista de mensajes.
    Si no hay texto, se salta el mensaje. Usa un LLM para estructurar los datos.
    Devuelve un listado de resultados con message_id, response_timestamp y processed_data.
    """
    results = []

    for invoice in messages:
        message_id = invoice.get('id')
        text = invoice.get('text')

        print(f"🔍 Processing message {message_id}...")

        if not text:
            print("⚠️ No text found in message. Skipping.")
            continue

        try:
            response = requests.post(
                "http://31.97.161.134:11434/api/generate",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "llama3:8b",
                    "prompt": (
                        "Extraé la siguiente información en formato JSON: "
                        "Fecha, CUITEmisor, CUITReceptor, PtoVenta, NroFactura, Monto, RazonSocialEmisor, RazonSocialReceptor "
                        f"para los datos contenidos en el siguiente set de datos:\n{text}.\n"
                        "No quiero más información, únicamente el JSON en formato plano."
                    ),
                    "stream": False
                }
            )
        except Exception as e:
            print(f"❌ Error calling LLM: {e}")
            continue

        if response.status_code != 200:
            print(f"❌ Error extracting invoice data: {response.text}")
            continue

        try:
            raw_response = response.json()
            raw_text = raw_response.get("response", "")

            # Limpiar texto si está envuelto en triple backticks
            if "```" in raw_text:
                parts = raw_text.split("```")
                if len(parts) >= 2:
                    raw_text = parts[1].strip()

            parsed_data = json.loads(raw_text)

            print(parsed_data)

            # Tomar el primer elemento si es una lista de un solo objeto
            if isinstance(parsed_data, list) and parsed_data:
                data = parsed_data[0]
            elif isinstance(parsed_data, dict):
                data = parsed_data
            else:
                print(f"⚠️ Unexpected data format for message {message_id}. Skipping.")
                continue

        except Exception as e:
            print(f"❌ Error parsing JSON response: {e}")
            continue

        # Validar que estén todas las claves requeridas
        required_keys = ["Fecha", "CUIT", "NroFactura", "Monto", "RazonSocial"]
        if not all(key in data for key in required_keys):
            print(f"⚠️ Incomplete data in message {message_id}. Missing keys.")
            continue

        results.append({
            "message_id": message_id,
            "response_timestamp": datetime.now().isoformat(),
            "processed_data": {
                "Fecha": data["Fecha"],
                "CUIT": data["CUIT"],
                "NroFactura": data["NroFactura"],
                "Monto": data["Monto"],
                "RazonSocial": data["RazonSocial"]
            }
        })

        #Insertar los valores en GSheets
        insert_invoice_data(results)

    return results
