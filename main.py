import json
import logging
import os
import sys
import time
import argparse
import pystray
from PIL import Image
from src.classifier import classify
from src.file_manager import move_and_rename
from src.document_parser import extract_first_page_text
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

# Devuelve la funcion callback que se ejecuta cuando el watcher detecta un PDF nuevo y estable
def make_processor(config: dict, logger: logging.Logger):
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
    parser = argparse.ArgumentParser(description="Smart-DocuSorter: Clasificador automático.")
    parser.add_argument(
        "--config", 
        default=CONFIG_PATH, 
        help="Ruta al archivo de configuración config.json"
    )
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Error: No se encontró el archivo de configuración en {args.config}")
        print("Copia config.example.json como config.json y edítalo.")
        sys.exit(1)

    config = load_config(args.config)
    logger = setup_logging(config["log_file"])

    processor = make_processor(config, logger)
    observer = start_watching(config["watch_folder"], processor)

    logger.info("Smart-DocuSorter iniciado en la bandeja del sistema.")

    # Se define dentro de main para poder acceder a la variable 'observer'
    def exit_action(icon, item):
        logger.info("Deteniendo Smart-DocuSorter...")
        observer.stop()
        icon.stop()

    try:
        image = Image.open("icono.png")
    except FileNotFoundError:
        print("Error: Necesitas un archivo 'icono.png' en la carpeta principal.")
        observer.stop()
        sys.exit(1)

    menu = pystray.Menu(pystray.MenuItem("Salir", exit_action))
    icon = pystray.Icon("DocuSorter", image, "Smart-DocuSorter", menu)
    
    try:
        icon.run() # Mantiene el programa abierto en segundo plano
    except KeyboardInterrupt:
        logger.info("Cierre forzado desde consola...")
        observer.stop()
        
    observer.join()

# Ejecución manual: python main.py --config mi_configuracion.json
if __name__ == "__main__": 
    main()