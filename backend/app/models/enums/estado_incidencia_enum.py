from enum import Enum


class EstadoIncidenciaEnum(str, Enum):
    """Ciclo de vida de una Incidencia, incluye PROGRAMADO para aperturas anticipadas."""

    RECIBIDO = "RECIBIDO"
    PROGRAMADO = "PROGRAMADO"
    EN_PROCESO = "EN_PROCESO"
    RESUELTO = "RESUELTO"
