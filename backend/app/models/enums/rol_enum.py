from enum import Enum


class RolEnum(str, Enum):
    """Roles del sistema usados para el control de acceso (RNF4)."""

    ADMINISTRADOR = "ADMINISTRADOR"
    DOCENTE = "DOCENTE"
    TECNICO = "TECNICO"
