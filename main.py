"""
main.py
Punto de entrada de Smart-DocuSorter.

En Windows esto NO es un daemon unix; corre como proceso en primer
plano (o en background con pythonw.exe / Task Scheduler, ver README).
"""

import json
import logging
import os
import sys
import time

from src.classifier import classify
from src.file_manager import move_and_rename
from src.pdf_parser import extract_first_page_text
from src.watcher import start_watching

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config(path: str = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def setup_logging(log_file: str):
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger("smart_docusorter")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def make_processor(config: dict, logger: logging.Logger):
    """
    Devuelve la funcion callback que se ejecuta cada vez que el
    watcher detecta un PDF nuevo y estable.
    """

    def process_pdf(pdf_path: str):
        logger.info("Nuevo PDF detectado: %s", pdf_path)

        text = extract_first_page_text(pdf_path)
        if not text.strip():
            logger.warning(
                "No se pudo extraer texto (posible PDF escaneado): %s", pdf_path
            )

        category, destination = classify(
            text, config["rules"], config["default_destination"]
        )

        try:
            final_path = move_and_rename(pdf_path, destination)
            logger.info("'%s' clasificado como '%s' -> %s", pdf_path, category, final_path)
        except Exception as exc:
            logger.error("Error al mover '%s': %s", pdf_path, exc)

    return process_pdf


def main():
    config = load_config()
    logger = setup_logging(config["log_file"])

    processor = make_processor(config, logger)
    observer = start_watching(config["watch_folder"], processor)

    logger.info("Smart-DocuSorter iniciado. Ctrl+C para detener.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Deteniendo Smart-DocuSorter...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
