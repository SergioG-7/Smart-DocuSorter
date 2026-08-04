"""
classifier.py
Normaliza el texto extraido y lo cruza contra las reglas de config.json
para determinar la categoria y carpeta destino.
"""

import logging
import unicodedata
from typing import Optional

logger = logging.getLogger("smart_docusorter")


def normalize(text: str) -> str:
    """
    Pasa a minusculas y elimina tildes/diacriticos.
    'Álgebra Lineal' -> 'algebra lineal'
    """
    text = text.lower()
    # Descompone caracteres acentuados (NFD) y descarta las marcas
    # de combinacion (categoria Unicode 'Mn'), lo que quita tildes
    # sin afectar el resto del texto (ñ se mantiene si no se separa).
    nfkd = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in nfkd if unicodedata.category(ch) != "Mn")


def classify(text: str, rules: list[dict], default_destination: str) -> tuple[str, str]:
    """
    Recibe el texto crudo de la primera pagina y la lista de reglas
    de config.json. Devuelve (categoria, carpeta_destino).

    Recorre las reglas en orden; la primera cuyo keyword aparezca en
    el texto normalizado gana. Si ninguna coincide, usa
    default_destination con categoria "Sin_Clasificar".
    """
    normalized_text = normalize(text)

    for rule in rules:
        category = rule["category"]
        keywords = rule.get("keywords", [])
        for keyword in keywords:
            if normalize(keyword) in normalized_text:
                logger.info("Clasificado como '%s' por keyword '%s'", category, keyword)
                return category, rule["destination"]

    logger.info("Sin coincidencias, usando destino por defecto")
    return "Sin_Clasificar", default_destination
