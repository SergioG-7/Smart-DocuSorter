"""
classifier.py
Normaliza el texto extraido y lo cruza contra las reglas de config.json
para determinar la categoria y carpeta destino.
"""

import logging
import unicodedata
import re

logger = logging.getLogger("smart_docusorter")


def normalize(text: str) -> str:
    """
    Pasa a minusculas y elimina tildes/diacriticos.
    'Álgebra Lineal' -> 'algebra lineal'
    """
    text = text.lower()
    nfkd = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in nfkd if unicodedata.category(ch) != "Mn")


def classify(text: str, rules: list[dict], default_destination: str) -> tuple[str, str]:
    """
    Recibe el texto crudo de la primera pagina y la lista de reglas
    de config.json. Devuelve (categoria, carpeta_destino).
    """
    normalized_text = normalize(text)

    for rule in rules:
        category = rule["category"]
        keywords = rule.get("keywords", [])
        for keyword in keywords:
            # Usamos \b para indicar "frontera de palabra" (word boundary)
            # Así 'iva' no coincidirá con 'oliva' ni 'privado'
            patron = r'\b' + re.escape(normalize(keyword)) + r'\b'
            
            if re.search(patron, normalized_text):
                logger.info("Clasificado como '%s' por keyword '%s'", category, keyword)
                return category, rule["destination"]

    logger.info("Sin coincidencias, usando destino por defecto")
    return "Sin_Clasificar", default_destination