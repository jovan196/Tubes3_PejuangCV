import pdfplumber

def extract_text_from_pdf(pdf_path):
    # Ekstrak seluruh teks dari file PDF dan menggabungkannya jadi satu string
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text