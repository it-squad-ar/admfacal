from PIL import Image
import pytesseract
import io
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_bytes):
    text = ""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"❌ Error reading PDF with fitz: {e}")
    return text.strip()

def process_invoices(emails):
    invoices = []

    for email in emails:
        print(f"📥 Processing email {email['id']}")
        for attachment in email.get('attachments', []):
            filename = attachment['filename']
            file_data = attachment['data']
            text = ""

            try:
                if filename.lower().endswith('.pdf'):
                    print("📄 PDF identified")
                    text = extract_text_from_pdf(file_data)

                elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
                    print("🖼️ Image identified")
                    image = Image.open(io.BytesIO(file_data))
                    text = pytesseract.image_to_string(image)

                if text.strip():
                    invoices.append({
                        'id': email['id'],
                        'filename': filename,
                        'text': text.strip()
                    })

            except Exception as e:
                print(f"❌ Error processing {filename} from {email['id']}: {e}")

    return invoices