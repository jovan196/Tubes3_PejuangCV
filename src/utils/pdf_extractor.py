import PyPDF2
import fitz
import os

class PDFExtractor:
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text with PyPDF2 from {pdf_path}: {e}")
            return ""

    def extract_text_pymupdf(self, pdf_path: str) -> str:
        try:
            text = ""
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text() + "\n"
            doc.close()
            return text.strip()
        except Exception as e:
            print(f"Error extracting text with PyMuPDF from {pdf_path}: {e}")
            return ""

    def extract_text(self, pdf_path: str, method: str = "auto") -> str:
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            return ""
        if not pdf_path.lower().endswith('.pdf'):
            print(f"File is not a PDF: {pdf_path}")
            return ""
        extracted_text = ""
        if method == "pypdf2":
            extracted_text = self.extract_text_pypdf2(pdf_path)
        elif method == "pymupdf":
            extracted_text = self.extract_text_pymupdf(pdf_path)
        elif method == "auto":
            extracted_text = self.extract_text_pymupdf(pdf_path)
            if not extracted_text or len(extracted_text.strip()) < 10:
                extracted_text = self.extract_text_pypdf2(pdf_path)
        extracted_text = self.clean_text(extracted_text)
        return extracted_text

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_line = line.strip()
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        cleaned_text = ' '.join(cleaned_lines)
        import re
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        return cleaned_text.strip()

    def extract_text_by_pages(self, pdf_path: str) -> list:
        if not os.path.exists(pdf_path):
            return []
        pages_text = []
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                pages_text.append(self.clean_text(page_text))
            doc.close()
            return pages_text
        except Exception as e:
            print(f"Error extracting text by pages from {pdf_path}: {e}")
            return []

    def get_pdf_info(self, pdf_path: str) -> dict:
        if not os.path.exists(pdf_path):
            return {}
        try:
            doc = fitz.open(pdf_path)
            info = {
                "page_count": len(doc),
                "metadata": doc.metadata,
                "file_size": os.path.getsize(pdf_path),
                "file_name": os.path.basename(pdf_path)
            }
            doc.close()
            return info
        except Exception as e:
            print(f"Error getting PDF info from {pdf_path}: {e}")
            return {}

    def is_valid_pdf(self, pdf_path: str) -> bool:
        try:
            doc = fitz.open(pdf_path)
            if len(doc) > 0:
                page = doc.load_page(0)
                text = page.get_text()
            doc.close()
            return True
        except Exception as e:
            print(f"Invalid PDF {pdf_path}: {e}")
            return False

    def extract_structured_data(self, pdf_path: str) -> dict:
        text = self.extract_text(pdf_path)
        if not text:
            return {}
        from utils.regex_extractor import RegexExtractor
        extractor = RegexExtractor()
        structured_data = extractor.extract_cv_info(text)
        metadata = self.get_pdf_info(pdf_path)
        structured_data['pdf_metadata'] = metadata
        structured_data['file_info'] = {
            'filename': os.path.basename(pdf_path),
            'file_size': os.path.getsize(pdf_path),
            'extraction_method': 'auto'
        }
        return structured_data