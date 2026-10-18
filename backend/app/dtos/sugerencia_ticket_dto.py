from dataclasses import dataclass

from app.models.enums import TipoFallaEnum


@dataclass(frozen=True)
class SugerenciaTicketDTO:
    """Datos que el chatbot propone para precargar el formulario de incidencia (RF3)."""

    id_laboratorio: int
    categoria: str
    tipo_falla: TipoFallaEnum
    descripcion: str
