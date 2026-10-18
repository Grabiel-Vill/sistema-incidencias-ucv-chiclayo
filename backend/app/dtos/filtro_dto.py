from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from app.exceptions import ValidacionException
from app.models.enums import EstadoIncidenciaEnum, TipoFallaEnum
from app.utils.date_utils import DateUtils

if TYPE_CHECKING:
    from app.models.incidencia import Incidencia


@dataclass(frozen=True)
class FiltroDTO:
    """Criterios opcionales para filtrar incidencias en bandejas y dashboards (RF4, RF5)."""

    fecha_desde: datetime | None = None
    fecha_hasta: datetime | None = None
    id_laboratorio: int | None = None
    tipo_falla: TipoFallaEnum | None = None
    estado: EstadoIncidenciaEnum | None = None
    id_tecnico: int | None = None

    def __post_init__(self) -> None:
        if self.fecha_desde and self.fecha_hasta and self.fecha_desde > self.fecha_hasta:
            raise ValidacionException("fecha_desde no puede ser posterior a fecha_hasta", campo="fecha_desde")

    def aplica_a(self, incidencia: "Incidencia") -> bool:
        if not DateUtils.esta_en_rango(incidencia.fecha_creacion, self.fecha_desde, self.fecha_hasta):
            return False
        if self.id_laboratorio is not None and incidencia.laboratorio.id_laboratorio != self.id_laboratorio:
            return False
        if self.tipo_falla is not None and incidencia.tipo_falla != self.tipo_falla:
            return False
        if self.estado is not None and incidencia.estado != self.estado:
            return False
        if self.id_tecnico is not None:
            if incidencia.tecnico_asignado is None or incidencia.tecnico_asignado.id_usuario != self.id_tecnico:
                return False
        return True
