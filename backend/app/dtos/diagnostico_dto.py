from dataclasses import dataclass

from app.models.enums import PrioridadEnum, TipoFallaEnum


@dataclass(frozen=True)
class DiagnosticoDTO:
    """Clasificacion que el AsistenteIA produce a partir de la descripcion en lenguaje natural (RF3)."""

    tipo_falla: TipoFallaEnum
    diagnostico: str
    prioridad: PrioridadEnum
