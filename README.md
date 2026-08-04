# Smart-DocuSorter

Vigila tu carpeta de Descargas, clasifica PDFs nuevos por palabras clave
y los renombra/mueve automaticamente.

## Instalación (Windows)

```powershell
cd smart-docusorter
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración

Edita `config.json`:

- `watch_folder`: ruta de tu carpeta de Descargas (usa `\\` o barras normales `/`, ambas funcionan en Python).
- `rules`: lista ordenada — la primera regla cuyo keyword aparezca en el texto gana. Pon las más específicas primero.
- `default_destination`: dónde va lo que no coincide con ninguna regla.

Reemplaza `<TU_USUARIO>` en las rutas por tu usuario real de Windows.

## Ejecutar

```powershell
python main.py
```

Corre en primer plano y loguea en consola + `logs/sorter.log`. Ctrl+C para detener.

### Correr en segundo plano sin ventana de consola

Esto **no es un daemon unix** — en Windows las opciones equivalentes son:

1. **pythonw.exe** (sin consola visible):
   ```powershell
   venv\Scripts\pythonw.exe main.py
   ```
2. **Task Scheduler**: crea una tarea "Al iniciar sesión" que ejecute
   `venv\Scripts\pythonw.exe` con argumento `main.py` y "Iniciar en"
   apuntando a la carpeta del proyecto. Así arranca solo al loguearte.

## Limitaciones conocidas

- PDFs escaneados sin capa de texto (solo imagen) devuelven texto vacío
  → van a `default_destination`. No hay OCR implementado.
- La clasificación es por primera coincidencia en orden de lista, no
  por mejor match — ordena tus reglas de más a menos específica.
- Si mueves manualmente un PDF a la carpeta vigilada (drag & drop),
  también se procesa; no distingue "descargado" de "movido ahí".
