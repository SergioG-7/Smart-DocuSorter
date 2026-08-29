import logging
import os
import docx
import pytesseract
from PIL import Image
import pdfplumber
from google import genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("smart_docusorter")

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

_client = None

def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY no configurada en .env")
        _client = genai.Client(api_key=api_key)
    return _client

def extract_text(file_path: str, max_pdf_pages: int = 3) -> str:
    ext = file_path.lower().split(".")[-1]
    text = ""
    try:
        if ext == "pdf":
            with pdfplumber.open(file_path) as pdf:
                chunks = []
                for page in pdf.pages[:max_pdf_pages]:
                    try:
                        chunks.append(page.extract_text() or "")
                    except Exception as page_exc:
                        logger.error("Error leyendo pagina de %s: %s", file_path, page_exc)
                text = "\n".join(chunks)
        elif ext == "docx":
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif ext in ["png", "jpg", "jpeg"]:
            text = pytesseract.image_to_string(Image.open(file_path))
    except Exception as exc:
        logger.error("Error leyendo %s: %s", file_path, exc)

    return text.strip()

def classify_with_ai(text: str, categories: list) -> str:
    if not text:
        return "Sin_Clasificar"
        
    prompt = (
        f"Actua como un clasificador de texto estricto. Lee el siguiente fragmento "
        f"y responde unicamente con el nombre de la categoria a la que pertenece: {categories}. "
        "Si el texto no encaja claramente con ninguna categoria de la lista, responde exactamente: Sin_Clasificar. "
        "No agregues introducciones ni explicaciones. "
        f"Texto a clasificar: {text[:1500]}"
    )
    
    try:
        chat = _get_client().chats.create(model='gemini-3.6-flash')
        response = chat.send_message(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.error("Error con la IA: %s", exc)
        return "Sin_Clasificar"