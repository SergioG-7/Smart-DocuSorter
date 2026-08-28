import os
import docx
import pytesseract
from PIL import Image
import pdfplumber
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(file_path: str) -> str:
    ext = file_path.lower().split(".")[-1]
    text = ""
    try:
        if ext == "pdf":
            with pdfplumber.open(file_path) as pdf:
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
        f"Actua como un clasificador de texto estricto. Lee el siguiente fragmento "
        f"y responde unicamente con el nombre de la categoria a la que pertenece: {categories}. "
        "Si el texto no encaja claramente con ninguna categoria de la lista, responde exactamente: Sin_Clasificar. "
        "No agregues introducciones ni explicaciones. "
        f"Texto a clasificar: {text[:1500]}"
    )
    
    try:
        chat = client.chats.create(model='gemini-3.6-flash')
        response = chat.send_message(prompt)
        return response.text.strip()
    except Exception as exc:
        print(f"Error con la IA: {exc}")
        return "Sin_Clasificar"