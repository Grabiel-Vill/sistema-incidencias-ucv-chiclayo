from enum import Enum


class FormatoEnum(str, Enum):
    """Formatos de exportacion soportados para los reportes administrativos."""

    PDF = "PDF"
    EXCEL = "EXCEL"
