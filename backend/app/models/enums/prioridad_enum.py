from enum import Enum


class PrioridadEnum(str, Enum):
    """Prioridad de atencion asignada a una Incidencia."""

    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"
