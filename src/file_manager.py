"""
file_manager.py
Renombra el PDF con el prefijo de fecha YYYY-MM y lo mueve a su
carpeta de destino final.
"""

import logging
import os
import shutil
from datetime import datetime

logger = logging.getLogger("smart_docusorter")


def build_new_filename(original_path: str) -> str:
    """
    'contrato_alquiler.pdf' -> '2026-08_contrato_alquiler.pdf'
    """
    date_prefix = datetime.now().strftime("%Y-%m")
    original_name = os.path.basename(original_path)
    return f"{date_prefix}_{original_name}"


def move_and_rename(original_path: str, destination_folder: str) -> str:
    """
    Crea destination_folder si no existe, renombra el archivo con
    fecha y lo mueve ahi. Si ya existe un archivo con ese nombre en
    destino, añade un sufijo numerico para no sobreescribir.
    Devuelve la ruta final del archivo.
    """
    os.makedirs(destination_folder, exist_ok=True)

    new_filename = build_new_filename(original_path)
    destination_path = os.path.join(destination_folder, new_filename)

    destination_path = _resolve_collision(destination_path)

    shutil.move(original_path, destination_path)
    logger.info("Movido '%s' -> '%s'", original_path, destination_path)
    return destination_path


def _resolve_collision(destination_path: str) -> str:
    """
    Si destination_path ya existe, inserta ' (n)' antes de la
    extension hasta encontrar un nombre libre.
    """
    if not os.path.exists(destination_path):
        return destination_path

    base, ext = os.path.splitext(destination_path)
    counter = 1
    candidate = f"{base} ({counter}){ext}"
    while os.path.exists(candidate):
        counter += 1
        candidate = f"{base} ({counter}){ext}"
    return candidate
