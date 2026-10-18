import uuid
from pathlib import Path

from app.exceptions import ValidacionException
from app.utils.validators import Validators

_EXTENSIONES_PERMITIDAS = (".jpg", ".jpeg", ".png", ".webp")
_DIRECTORIO_POR_DEFECTO = Path(__file__).resolve().parents[2] / "storage" / "evidencias"


class FileStorage:
    """Guarda y elimina imagenes de evidencia en storage/evidencias (RF1: evidencia fotografica)."""

    def __init__(self, directorio_base: Path | str | None = None):
        self._directorio_base = Path(directorio_base) if directorio_base else _DIRECTORIO_POR_DEFECTO
        self._directorio_base.mkdir(parents=True, exist_ok=True)

    def guardar_imagen(self, nombre_original: str, contenido: bytes) -> str:
        if not Validators.tiene_extension_valida(nombre_original, _EXTENSIONES_PERMITIDAS):
            raise ValidacionException(
                f"Extension no permitida, use una de {_EXTENSIONES_PERMITIDAS}", campo="nombre_original"
            )
        extension = Path(nombre_original).suffix.lower()
        nombre_unico = f"{uuid.uuid4().hex}{extension}"
        ruta = self._directorio_base / nombre_unico
        ruta.write_bytes(contenido)
        return f"evidencias/{nombre_unico}"

    def eliminar_imagen(self, ruta_relativa: str) -> None:
        ruta = (self._directorio_base.parent / ruta_relativa).resolve()
        if self._directorio_base.resolve() not in ruta.parents:
            raise ValidacionException("Ruta de evidencia fuera del almacenamiento permitido", campo="ruta_relativa")
        ruta.unlink(missing_ok=True)
