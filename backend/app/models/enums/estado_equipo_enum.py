from enum import Enum


class EstadoEquipoEnum(str, Enum):
    """Estado operativo de un Equipo de laboratorio."""

    OPERATIVO = "OPERATIVO"
    DEFECTUOSO = "DEFECTUOSO"
    EN_MANTENIMIENTO = "EN_MANTENIMIENTO"
