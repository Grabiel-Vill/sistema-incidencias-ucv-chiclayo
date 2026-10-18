from enum import Enum


class TipoFallaEnum(str, Enum):
    """Categoria tecnica de la falla reportada en una Incidencia."""

    HARDWARE = "HARDWARE"
    RED = "RED"
    SOFTWARE = "SOFTWARE"
    ELECTRICIDAD = "ELECTRICIDAD"
    ILUMINACION = "ILUMINACION"
