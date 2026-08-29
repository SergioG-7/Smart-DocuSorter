from pathlib import Path

from src.file_manager import build_new_filename, move_and_rename, _resolve_collision
from src.document_parser import classify_with_ai


def test_build_new_filename():
    nombre = build_new_filename("contrato_alquiler.pdf")
    assert nombre.endswith("_contrato_alquiler.pdf")
    assert len(nombre.split("_")[0]) == 7  # YYYY-MM


def test_move_and_rename(tmp_path: Path):
    origen = tmp_path / "factura.pdf"
    origen.write_text("dummy")
    destino_dir = tmp_path / "Facturas"

    ruta_final = move_and_rename(str(origen), str(destino_dir))

    assert Path(ruta_final).exists()
    assert not origen.exists()
    assert Path(ruta_final).parent == destino_dir


def test_resolve_collision(tmp_path: Path):
    archivo = tmp_path / "doc.pdf"
    archivo.write_text("dummy")

    candidato = _resolve_collision(str(archivo))

    assert candidato != str(archivo)
    assert "(1)" in candidato


def test_classify_with_ai_texto_vacio():
    assert classify_with_ai("", ["Facturas", "Contratos"]) == "Sin_Clasificar"
