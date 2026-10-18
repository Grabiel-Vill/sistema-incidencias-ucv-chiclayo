from __future__ import annotations

from datetime import datetime

from app.exceptions import ValidacionException

_EXTENSIONES_VALIDAS = (".jpg", ".jpeg", ".png", ".webp")


class Evidencia:
    """Fotografia adjunta a una Incidencia o una NotaTecnica (composicion: vive dentro de su contenedor)."""

    def __init__(self, id_evidencia: int, url_imagen: str, fecha_carga: datetime | None = None):
        self._id_evidencia = id_evidencia
        self.url_imagen = url_imagen
        self._fecha_carga = fecha_carga or datetime.now()
        self._id_incidencia: int | None = None

    @property
    def id_evidencia(self) -> int:
        return self._id_evidencia

    @property
    def url_imagen(self) -> str:
        return self._url_imagen

    @url_imagen.setter
    def url_imagen(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValidacionException("La URL de la imagen no puede estar vacia", campo="url_imagen")
        self._url_imagen = valor.strip()

    @property
    def fecha_carga(self) -> datetime:
        return self._fecha_carga

    def es_formato_valido(self) -> bool:
        return self._url_imagen.lower().endswith(_EXTENSIONES_VALIDAS)

    @property
    def id_incidencia(self) -> int | None:
        return self._id_incidencia

    def asociar_incidencia(self, id_incidencia: int) -> None:
        self._id_incidencia = id_incidencia

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Evidencia) and self._id_evidencia == other._id_evidencia

    def __hash__(self) -> int:
        return hash(self._id_evidencia)

    def __repr__(self) -> str:
        return f"Evidencia(id={self._id_evidencia}, url_imagen='{self._url_imagen}')"
