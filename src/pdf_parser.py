"""
pdf_parser.py
Extrae el texto de la primera pagina de un PDF.

Uso pdfplumber en vez de PyPDF2 porque su extraccion de texto es mas
fiable en PDFs con layouts complejos (tablas, columnas). Si el PDF esta
escaneado (imagen sin capa de texto), esto devolvera cadena vacia; no
hay OCR aqui.
"""

import logging

import pdfplumber

logger = logging.getLogger("smart_docusorter")


def extract_first_page_text(pdf_path: str) -> str:
    """
    Devuelve el texto de la primera pagina del PDF, o "" si falla
    la extraccion o el PDF no tiene texto (ej. escaneado sin OCR).
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                logger.warning("PDF sin paginas: %s", pdf_path)
                return ""
            first_page = pdf.pages[0]
            text = first_page.extract_text() or ""
            return text
    except Exception as exc:
        # Cubre PDFs corruptos, protegidos con password, en uso por
        # otro proceso (descarga incompleta), etc.
        logger.error("Error al leer PDF %s: %s", pdf_path, exc)
        return ""
