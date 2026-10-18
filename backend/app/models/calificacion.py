from __future__ import annotations

from datetime import datetime

from app.exceptions import ValidacionException


class Calificacion:
    """Calificacion que un Docente deja sobre un Tecnico al cerrar un ticket RESUELTO (1 por incidencia)."""

    def __init__(
        self,
        id_calificacion: int,
        id_incidencia: int,
        id_docente: int,
        id_tecnico: int,
        estrellas: int,
        comentario: str | None = None,
        fecha: datetime | None = None,
    ):
        self._id_calificacion = id_calificacion
        self._id_incidencia = id_incidencia
        self._id_docente = id_docente
        self._id_tecnico = id_tecnico
        self.estrellas = estrellas
        self.comentario = comentario
        self._fecha = fecha or datetime.now()

    @property
    def id_calificacion(self) -> int:
        return self._id_calificacion

    @property
    def id_incidencia(self) -> int:
        return self._id_incidencia

    @property
    def id_docente(self) -> int:
        return self._id_docente

    @property
    def id_tecnico(self) -> int:
        return self._id_tecnico

    @property
    def estrellas(self) -> int:
        return self._estrellas

    @estrellas.setter
    def estrellas(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor < 1 or valor > 5:
            raise ValidacionException("Las estrellas deben ser un entero entre 1 y 5", campo="estrellas")
        self._estrellas = valor

    @property
    def comentario(self) -> str | None:
        return self._comentario

    @comentario.setter
    def comentario(self, valor: str | None) -> None:
        self._comentario = valor.strip() if valor and valor.strip() else None

    @property
    def fecha(self) -> datetime:
        return self._fecha

    def __repr__(self) -> str:
        return f"Calificacion(incidencia={self._id_incidencia}, estrellas={self._estrellas})"
