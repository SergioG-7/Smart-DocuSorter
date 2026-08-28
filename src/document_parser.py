import docx
import pytesseract
from PIL import Image
import pdfplumber

# Ruta donde se instala Tesseract en Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(file_path: str) -> str:
    ext = file_path.lower().split(".")[-1]

    if ext == "pdf":
        # Extrae texto nativo primero
        with pdfplumber.open(file_path) as pdf:
            text = pdf.pages[0].extract_text() or ""
            return text

    elif ext == "docx":
        # Une todos los parrafos del Word
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    elif ext in ["png", "jpg", "jpeg"]:
        # Lee el texto de la imagen
        return pytesseract.image_to_string(Image.open(file_path))

    return ""