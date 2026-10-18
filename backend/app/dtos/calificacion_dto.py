from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.calificacion import Calificacion


@dataclass(frozen=True)
class CalificacionRespuestaDTO:
    """Calificacion de un ticket resuelto, lista para ser serializada."""

    id_calificacion: int
    id_incidencia: int
    id_docente: int
    id_tecnico: int
    estrellas: int
    comentario: str | None
    fecha: datetime

    @classmethod
    def desde_calificacion(cls, calificacion: "Calificacion") -> "CalificacionRespuestaDTO":
        return cls(
            id_calificacion=calificacion.id_calificacion,
            id_incidencia=calificacion.id_incidencia,
            id_docente=calificacion.id_docente,
            id_tecnico=calificacion.id_tecnico,
            estrellas=calificacion.estrellas,
            comentario=calificacion.comentario,
            fecha=calificacion.fecha,
        )
