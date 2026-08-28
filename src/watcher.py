"""
Vigila la carpeta de Descargas usando watchdog (bajo consumo de CPU,
basado en eventos nativos del sistema de archivos, no polling).

Detalle importante en Windows/Chrome/Edge: el navegador suele escribir
primero un archivo temporal (.crdownload / .tmp) y, al terminar la
descarga, lo renombra a .pdf. Por eso escuchamos tanto on_created
como on_moved, y en ambos casos esperamos a que el tamaño del archivo
se estabilice antes de procesarlo (evita leer un PDF a medio escribir).
"""

import logging
import os
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger("smart_docusorter")


class PDFHandler(FileSystemEventHandler):
    def __init__(self, on_pdf_ready):
        super().__init__()
        self.on_pdf_ready = on_pdf_ready
        self._seen = set()

    def on_created(self, event):
        self._handle_event(event)

    def on_moved(self, event):
        # dest_path es el nombre final tras el rename (ej. quitar .crdownload)
        if not event.is_directory and event.dest_path.lower().endswith(".pdf"):
            self._process_when_stable(event.dest_path)

    def _handle_event(self, event):
        if event.is_directory or not event.src_path.lower().endswith(".pdf"):
            return
        self._process_when_stable(event.src_path)

    def _process_when_stable(self, path: str):
        if path in self._seen:
            return
        if not self._wait_until_stable(path):
            logger.warning("Archivo no estabilizo, se ignora: %s", path)
            return
        self._seen.add(path)
        self.on_pdf_ready(path)

    @staticmethod
    def _wait_until_stable(path: str, checks: int = 3, interval: float = 1.0) -> bool:
        """
        Espera hasta que el tamaño del archivo no cambie durante
        'checks' lecturas consecutivas separadas por 'interval'
        segundos. Devuelve False si el archivo desaparece o si tras
        un numero razonable de intentos sigue cambiando de tamaño.
        """
        stable_count = 0
        last_size = -1
        attempts = 0
        max_attempts = 30  # ~30s de margen para descargas grandes

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


def start_watching(folder: str, on_pdf_ready) -> Observer:
    """
    Lanza el Observer de watchdog sobre 'folder' y lo devuelve para
    que el llamador controle su ciclo de vida (join/stop).
    """
    os.makedirs(folder, exist_ok=True)
    handler = PDFHandler(on_pdf_ready)
    observer = Observer()
    observer.schedule(handler, folder, recursive=False)
    observer.start()
    logger.info("Vigilando carpeta: %s", folder)
    return observer
