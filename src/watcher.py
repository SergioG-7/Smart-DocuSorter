# Vigila descargas y eventos del sistema sin consumir mucha CPU
# Espera a que termine la descarga antes de procesar el archivo

import logging
import os
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger("smart_docusorter")


class DocumentHandler(FileSystemEventHandler):
    def __init__(self, on_file_ready):
        super().__init__()
        self.on_file_ready = on_file_ready
        self._seen = set()

    def on_created(self, event):
        self._handle_event(event)

    def on_moved(self, event):
        # Detecta archivos soportados tras ser renombrados (ej. fin de .crdownload)
        if not event.is_directory and event.dest_path.lower().endswith((".pdf", ".docx", ".jpg", ".jpeg", ".png")):
            self._process_when_stable(event.dest_path)

    def _handle_event(self, event):
        # Filtra solo las extensiones que sabemos procesar
        if event.is_directory or not event.src_path.lower().endswith((".pdf", ".docx", ".jpg", ".jpeg", ".png")):
            return
        self._process_when_stable(event.src_path)

    def _process_when_stable(self, path: str):
        if path in self._seen:
            return
        if not self._wait_until_stable(path):
            logger.warning("Archivo no estabilizado, se ignora: %s", path)
            return
        self._seen.add(path)
        self.on_file_ready(path)

    @staticmethod
    def _wait_until_stable(path: str, checks: int = 3, interval: float = 1.0) -> bool:
        # Comprueba que el archivo deje de cambiar de tamaño durante 3 segundos
        stable_count = 0
        last_size = -1
        attempts = 0
        max_attempts = 30  # Margen de 30 segundos para descargas lentas

        while stable_count < checks and attempts < max_attempts:
            if not os.path.exists(path):
                return False
            try:
                current_size = os.path.getsize(path)
            except OSError:
                return False

            if current_size == last_size:
                stable_count += 1
            else:
                stable_count = 0
                last_size = current_size

            attempts += 1
            time.sleep(interval)

        return stable_count >= checks


def start_watching(folder: str, on_file_ready) -> Observer:
    # Lanza el monitor en la carpeta configurada
    os.makedirs(folder, exist_ok=True)
    handler = DocumentHandler(on_file_ready)
    observer = Observer()
    observer.schedule(handler, folder, recursive=False)
    observer.start()
    logger.info("Vigilando carpeta: %s", folder)
    return observer