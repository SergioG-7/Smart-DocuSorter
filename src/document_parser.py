import os
import docx
import pytesseract
from PIL import Image
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configuración de IA y OCR
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(file_path: str) -> str:
    ext = file_path.lower().split(".")[-1]
    text = ""

    try:
        if ext == "pdf":
            with pdfplumber.open(file_path) as pdf:
                # Extrae solo la primera página
                text = pdf.pages[0].extract_text() or ""
        elif ext == "docx":
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif ext in ["png", "jpg", "jpeg"]:
            text = pytesseract.image_to_string(Image.open(file_path))
    except Exception as exc:
        print(f"Error leyendo {file_path}: {exc}")
        
    return text.strip()

def classify_with_ai(text: str, categories: list) -> str:
    if not text:
        return "Sin_Clasificar"
        
    prompt = (
        f"Clasifica este texto en UNA sola de estas categorias: {categories}. "
        "Devuelve SOLO el nombre exacto de la categoria. "
        f"Texto: {text[:1500]}"
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        print(f"Error con la IA: {exc}")
        return "Sin_Clasificar"