from enum import Enum


class TipoRequerimientoEnum(str, Enum):
    """Distingue una falla tecnica de una solicitud de apertura anticipada (RF1)."""

    FALLA_TECNICA = "FALLA_TECNICA"
    APERTURA_ANTICIPADA = "APERTURA_ANTICIPADA"
