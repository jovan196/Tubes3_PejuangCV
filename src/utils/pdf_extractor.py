# utils/pdf_extractor.py
import PyPDF2
import fitz  # PyMuPDF
import os
from typing import Optional

class PDFExtractor:
    """
    Utility class untuk ekstraksi teks dari file PDF.
    Mendukung multiple methods untuk memastikan ekstraksi yang optimal.
    """
    
    def __init__(self):
        pass
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """
        Ekstraksi teks menggunakan PyPDF2.
        
        Args:
            pdf_path (str): Path ke file PDF
            
        Returns:
            str: Teks yang diekstrak dari PDF
        """
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
        """
        Ekstraksi teks menggunakan PyMuPDF (fitz).
        
        Args:
            pdf_path (str): Path ke file PDF
            
        Returns:
            str: Teks yang diekstrak dari PDF
        """
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
        """
        Ekstraksi teks dari PDF dengan method yang dapat dipilih.
        
        Args:
            pdf_path (str): Path ke file PDF
            method (str): Method ekstraksi ("pypdf2", "pymupdf", "auto")
            
        Returns:
            str: Teks yang diekstrak dari PDF
        """
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
            # Try PyMuPDF first (generally better), fallback to PyPDF2
            extracted_text = self.extract_text_pymupdf(pdf_path)
            
            if not extracted_text or len(extracted_text.strip()) < 10:
                print("PyMuPDF extraction failed or returned minimal text, trying PyPDF2...")
                extracted_text = self.extract_text_pypdf2(pdf_path)
        
        # Clean and normalize text
        extracted_text = self.clean_text(extracted_text)
        
        return extracted_text
    
    def clean_text(self, text: str) -> str:
        """
        Membersihkan dan menormalisasi teks hasil ekstraksi.
        
        Args:
            text (str): Teks mentah hasil ekstraksi
            
        Returns:
            str: Teks yang telah dibersihkan
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Strip whitespace from each line
            cleaned_line = line.strip()
            
            # Skip empty lines
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        # Join lines with single space
        cleaned_text = ' '.join(cleaned_lines)
        
        # Replace multiple spaces with single space
        import re
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text.strip()
    
    def extract_text_by_pages(self, pdf_path: str) -> list:
        """
        Ekstraksi teks per halaman dari PDF.
        
        Args:
            pdf_path (str): Path ke file PDF
            
        Returns:
            list: List berisi teks dari setiap halaman
        """
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
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
        """
        Mendapatkan informasi metadata dari PDF.
        
        Args:
            pdf_path (str): Path ke file PDF
            
        Returns:
            dict: Informasi metadata PDF
        """
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
        """
        Memeriksa apakah file PDF valid dan dapat dibaca.
        
        Args:
            pdf_path (str): Path ke file PDF
            
        Returns:
            bool: True jika PDF valid
        """
        try:
            doc = fitz.open(pdf_path)
            # Try to access first page
            if len(doc) > 0:
                page = doc.load_page(0)
                text = page.get_text()
            doc.close()
            return True
            
        except Exception as e:
            print(f"Invalid PDF {pdf_path}: {e}")
            return False
    
    def extract_text_with_formatting(self, pdf_path: str) -> dict:
        """
        Ekstraksi teks dengan mempertahankan beberapa informasi formatting.
        
        Args:
            pdf_path (str): Path ke file PDF
            
        Returns:
            dict: Dictionary berisi teks dan informasi formatting
        """
        if not os.path.exists(pdf_path):
            return {"text": "", "formatting": []}
        
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            formatting_info = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get text with font information
                text_dict = page.get_text("dict")
                
                for block in text_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"]
                                font_size = span["size"]
                                font_flags = span["flags"]
                                
                                full_text += text
                                
                                formatting_info.append({
                                    "text": text,
                                    "font_size": font_size,
                                    "is_bold": bool(font_flags & 2**4),
                                    "is_italic": bool(font_flags & 2**1),
                                    "page": page_num + 1
                                })
            
            doc.close()
            
            return {
                "text": self.clean_text(full_text),
                "formatting": formatting_info
            }
            
        except Exception as e:
            print(f"Error extracting formatted text from {pdf_path}: {e}")
            return {"text": "", "formatting": []}
    
    def batch_extract(self, pdf_directory: str) -> dict:
        """
        Ekstraksi teks dari multiple PDF files dalam satu directory.
        
        Args:
            pdf_directory (str): Path ke directory berisi PDF files
            
        Returns:
            dict: Dictionary dengan filename sebagai key dan extracted text sebagai value
        """
        if not os.path.exists(pdf_directory):
            print(f"Directory not found: {pdf_directory}")
            return {}
        
        results = {}
        
        for filename in os.listdir(pdf_directory):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, filename)
                try:
                    text = self.extract_text(pdf_path)
                    results[filename] = text
                    print(f"Extracted text from: {filename}")
                except Exception as e:
                    print(f"Failed to extract from {filename}: {e}")
                    results[filename] = ""
        
        return results
    
    def extract_metadata(self, pdf_path: str) -> dict:
        """
        Extract metadata from PDF file.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            dict: PDF metadata information
        """
        if not os.path.exists(pdf_path):
            return {}
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata = {
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'subject': pdf_reader.metadata.get('/Subject', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                    'producer': pdf_reader.metadata.get('/Producer', ''),
                    'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                    'modification_date': pdf_reader.metadata.get('/ModDate', ''),
                    'page_count': len(pdf_reader.pages),
                    'file_size': os.path.getsize(pdf_path)
                }
                
                return metadata
        except Exception as e:
            print(f"Error extracting metadata from {pdf_path}: {e}")
            return {}
    
    def extract_images_info(self, pdf_path: str) -> list:
        """
        Extract information about images in PDF.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            list: List of image information
        """
        if not os.path.exists(pdf_path):
            return []
        
        try:
            doc = fitz.open(pdf_path)
            images_info = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    images_info.append({
                        'page': page_num + 1,
                        'index': img_index,
                        'xref': img[0],
                        'smask': img[1],
                        'width': img[2],
                        'height': img[3],
                        'bpc': img[4],
                        'colorspace': img[5],
                        'alt': img[6],
                        'name': img[7],
                        'filter': img[8]
                    })
            
            doc.close()
            return images_info
            
        except Exception as e:
            print(f"Error extracting images info from {pdf_path}: {e}")
            return []
    
    def search_text_in_pdf(self, pdf_path: str, search_term: str) -> list:
        """
        Search for specific text in PDF and return locations.
        
        Args:
            pdf_path (str): Path to PDF file
            search_term (str): Term to search for
            
        Returns:
            list: List of search results with page and position info
        """
        if not os.path.exists(pdf_path):
            return []
        
        try:
            doc = fitz.open(pdf_path)
            results = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_instances = page.search_for(search_term)
                
                for inst in text_instances:
                    results.append({
                        'page': page_num + 1,
                        'bbox': inst,
                        'text': search_term
                    })
            
            doc.close()
            return results
            
        except Exception as e:
            print(f"Error searching text in {pdf_path}: {e}")
            return []
    
    def extract_tables(self, pdf_path: str) -> list:
        """
        Extract table-like structures from PDF.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            list: List of potential table data
        """
        if not os.path.exists(pdf_path):
            return []
        
        try:
            doc = fitz.open(pdf_path)
            tables = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get text with position information
                text_dict = page.get_text("dict")
                
                # Simple table detection based on text alignment
                potential_tables = []
                for block in text_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            line_text = ""
                            for span in line["spans"]:
                                line_text += span["text"]
                            
                            # Detect potential table rows (simple heuristic)
                            if "\t" in line_text or "  " in line_text:
                                potential_tables.append({
                                    'page': page_num + 1,
                                    'text': line_text.strip(),
                                    'bbox': line["bbox"]
                                })
                
                if potential_tables:
                    tables.extend(potential_tables)
            
            doc.close()
            return tables
            
        except Exception as e:
            print(f"Error extracting tables from {pdf_path}: {e}")
            return []
    
    def convert_pdf_to_images(self, pdf_path: str, output_dir: str = None, dpi: int = 150) -> list:
        """
        Convert PDF pages to images.
        
        Args:
            pdf_path (str): Path to PDF file
            output_dir (str): Directory to save images
            dpi (int): Resolution for images
            
        Returns:
            list: List of image file paths
        """
        if not os.path.exists(pdf_path):
            return []
        
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        try:
            doc = fitz.open(pdf_path)
            image_paths = []
            
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Create image matrix for higher resolution
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=mat)
                
                # Save image
                image_path = os.path.join(output_dir, f"{base_name}_page_{page_num + 1}.png")
                pix.save(image_path)
                image_paths.append(image_path)
                
                pix = None  # Free memory
            
            doc.close()
            return image_paths
            
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return []
    
    def optimize_pdf_text_extraction(self, pdf_path: str) -> str:
        """
        Optimized text extraction with multiple fallback methods.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            str: Extracted text using best available method
        """
        methods = [
            ("PyMuPDF", self.extract_text_pymupdf),
            ("PyPDF2", self.extract_text_pypdf2),
        ]
        
        best_text = ""
        best_score = 0
        
        for method_name, method_func in methods:
            try:
                text = method_func(pdf_path)
                
                # Score based on text length and content quality
                score = len(text)
                if text:
                    # Bonus for having common CV keywords
                    cv_keywords = ['experience', 'education', 'skills', 'work', 'university', 'graduate']
                    for keyword in cv_keywords:
                        if keyword.lower() in text.lower():
                            score += 100
                
                if score > best_score:
                    best_text = text
                    best_score = score
                    
            except Exception as e:
                print(f"Method {method_name} failed: {e}")
                continue
        
        return best_text if best_text else ""
    
    def extract_structured_data(self, pdf_path: str) -> dict:
        """
        Extract structured data from CV PDF.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            dict: Structured CV data
        """
        text = self.extract_text(pdf_path)
        
        if not text:
            return {}
        
        # Use regex extractor for structured data
        from utils.regex_extractor import RegexExtractor
        extractor = RegexExtractor()
        
        structured_data = extractor.extract_cv_info(text)
        
        # Add PDF metadata
        metadata = self.get_pdf_info(pdf_path)
        structured_data['pdf_metadata'] = metadata
        
        # Add file information
        structured_data['file_info'] = {
            'filename': os.path.basename(pdf_path),
            'file_size': os.path.getsize(pdf_path),
            'extraction_method': 'auto'
        }
        
        return structured_data