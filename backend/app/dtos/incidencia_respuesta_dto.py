from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from app.models.enums import EstadoIncidenciaEnum, PrioridadEnum, TipoFallaEnum

if TYPE_CHECKING:
    from app.models.incidencia import Incidencia


@dataclass(frozen=True)
class IncidenciaRespuestaDTO:
    """Vista de seguimiento de un ticket para el docente: estado, tecnico asignado y notas publicas (RF2)."""

    id_incidencia: int
    codigo_ticket: str
    descripcion: str
    tipo_falla: TipoFallaEnum | None
    estado: EstadoIncidenciaEnum
    prioridad: PrioridadEnum
    fecha_creacion: datetime
    fecha_atencion: datetime | None
    fecha_resolucion: datetime | None
    tecnico_asignado: str | None = None
    notas_publicas: list[str] = field(default_factory=list)
    subcategoria: str | None = None
    id_laboratorio: int | None = None
    laboratorio: str | None = None
    id_tecnico_asignado: int | None = None
    id_docente: int | None = None
    docente: str | None = None
    fecha_hora_apertura: datetime | None = None
    tipo_requerimiento: str | None = None
    id_equipo: int | None = None
    equipo: str | None = None
    calificada: bool = False

    @classmethod
    def desde_incidencia(cls, incidencia: "Incidencia") -> "IncidenciaRespuestaDTO":
        return cls(
            id_incidencia=incidencia.id_incidencia,
            codigo_ticket=incidencia.codigo_ticket,
            descripcion=incidencia.descripcion,
            tipo_falla=incidencia.tipo_falla,
            estado=incidencia.estado,
            prioridad=incidencia.prioridad,
            fecha_creacion=incidencia.fecha_creacion,
            fecha_atencion=incidencia.fecha_atencion,
            fecha_resolucion=incidencia.fecha_resolucion,
            tecnico_asignado=incidencia.tecnico_asignado.nombre_completo if incidencia.tecnico_asignado else None,
            notas_publicas=[nota.contenido for nota in incidencia.notas_tecnicas if not nota.es_privado],
            subcategoria=incidencia.subcategoria,
            id_laboratorio=incidencia.laboratorio.id_laboratorio,
            laboratorio=incidencia.laboratorio.nombre,
            id_tecnico_asignado=incidencia.tecnico_asignado.id_usuario if incidencia.tecnico_asignado else None,
            id_docente=incidencia.docente.id_usuario,
            docente=incidencia.docente.nombre_completo,
            fecha_hora_apertura=incidencia.fecha_hora_apertura,
            tipo_requerimiento=incidencia.tipo_requerimiento.value,
            id_equipo=incidencia.equipo.id_equipo if incidencia.equipo else None,
            equipo=incidencia.equipo.tipo_equipo if incidencia.equipo else None,
        )
