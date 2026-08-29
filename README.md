# Smart-DocuSorter

Organizador automático de archivos en segundo plano con clasificación semántica mediante IA y soporte de OCR para imágenes y documentos.

Monitorea tu carpeta de Descargas en tiempo real, extrae el contenido de archivos nuevos (PDF, Word, Imágenes) y los clasifica y mueve automáticamente a sus carpetas correspondientes según su significado conceptual.

---

## Características

* **Clasificación semántica con IA:** Utiliza el modelo `gemini-3.6-flash` de Google para comprender el contexto de los documentos en lugar de depender de palabras clave rígidas.
* **Soporte multiformato:** Procesa archivos `.pdf`, `.docx`, `.png`, `.jpg` y `.jpeg`.
* **OCR Integrado:** Extrae texto de imágenes escaneadas o capturas de pantalla mediante Tesseract OCR.
* **Monitorización no bloqueante:** Corre en segundo plano y se oculta en la bandeja del sistema (System Tray) con bajo impacto de CPU gracias a eventos nativos del sistema de archivos (`watchdog`).
* **Integridad de descargas:** Detecta y espera a que terminen las descargas del navegador (archivos temporales `.crdownload` o `.tmp`) antes de iniciar el procesamiento.

---

## Requisitos previos

1. **Python 3.10 o superior**
2. **Tesseract OCR (Windows):** Descarga e instala el binario oficial desde [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki). La ruta por defecto esperada por el código es:
   `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. **Clave de API de Gemini:** Obtén una API Key gratuita desde [Google AI Studio](https://aistudio.google.com/).

---

## Instalación (Windows)

1. Clona este repositorio y entra en la carpeta del proyecto:
   ```powershell
   git clone [https://github.com/SergioG-7/DocuSorter.git](https://github.com/SergioG-7/DocuSorter.git)
   cd DocuSorter
   ```

2. Crea y activa un entorno virtual:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instala todas las dependencias requeridas:
   ```powershell
   pip install -r requirements.txt
   ```

4. Configura tus variables de entorno creando un archivo `.env` en la raíz del proyecto:
   ```env
   GEMINI_API_KEY=tu_clave_api_aqui
   ```

---

## Configuración

Edita tu archivo `config.json` para definir tus rutas y categorías:

```json
{
  "watch_folder": "C:\\Users\\<TU_USUARIO>\\Downloads",
  "poll_interval_seconds": 2,
  "log_file": "logs/sorter.log",
  "rules": [
    {
      "category": "Mates",
      "destination": "C:\\Users\\<TU_USUARIO>\\Documentos\\Uni\\Mates"
    },
    {
      "category": "Facturas",
      "destination": "C:\\Users\\<TU_USUARIO>\\Documentos\\Facturas"
    },
    {
      "category": "Contratos",
      "destination": "C:\\Users\\<TU_USUARIO>\\Documentos\\Contratos"
    }
  ],
  "default_destination": "C:\\Users\\<TU_USUARIO>\\Documentos\\Sin_Clasificar"
}
```

* `watch_folder`: Ruta de la carpeta vigilada (usa `\\` o barras normales `/`).
* `rules`: Lista de categorías semánticas que la IA reconocerá y las rutas donde moverá los archivos asociados.
* `default_destination`: Carpeta de descarte para documentos cuyo contenido no encaje en ninguna de las reglas definidas.
* Reemplaza `<TU_USUARIO>` en las rutas por tu usuario real de Windows.

---

## Ejecución

### 1. Ejecución estándar con consola

```powershell
python main.py
```

Corre en primer plano, muestra la actividad en tiempo real y registra los eventos en `logs/sorter.log`. Aparecerá un icono en la bandeja del sistema (junto al reloj de Windows). Para cerrarlo de forma limpia, haz clic derecho sobre el icono y selecciona **Salir**, o presiona `Ctrl+C` en la terminal.

### 2. Ejecutar en segundo plano sin ventana de consola

Al no ser un daemon de Unix, en Windows dispones de dos opciones equivalentes:

* **Opción A (pythonw.exe):** Ejecútalo sin levantar ventana de terminal:
  ```powershell
  venv\Scripts\pythonw.exe main.py
  ```
* **Opción B (Programador de tareas de Windows):** Crea una tarea que se active "Al iniciar sesión", configurando la acción para que ejecute `venv\Scripts\pythonw.exe` con el argumento `main.py`, indicando en "Iniciar en" la ruta absoluta de la carpeta de tu proyecto. De este modo se iniciará automáticamente cada vez que inicies sesión.

---

## Limitaciones y consideraciones

* Si mueves manualmente un archivo admitido a la carpeta vigilada mediante arrastrar y soltar (drag & drop), el monitor lo procesará de igual forma, ya que el sistema de eventos no distingue entre descargas finalizadas y traslados manuales.
* Las imágenes con baja resolución, caligrafía ilegible o texto excesivamente borroso pueden generar fallos de lectura en el motor de Tesseract OCR, derivando el documento a `default_destination`.
* El plan gratuito de la API de Gemini aplica límites por minuto/día; si se procesan decenas de archivos simultáneamente, las solicitudes excedentes se catalogarán temporalmente como `Sin_Clasificar`.

---

## Tests y CI

El proyecto incluye pruebas unitarias en `tests/` (pytest) para la lógica de renombrado, movimiento y resolución de colisiones de archivos.

```powershell
python -m pytest -v
```

Cada push o pull request a `main`/`master` ejecuta estas pruebas automáticamente mediante GitHub Actions (`.github/workflows/ci.yml`).