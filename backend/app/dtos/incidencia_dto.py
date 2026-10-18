from dataclasses import dataclass
from datetime import datetime

from app.exceptions import ValidacionException
from app.models.enums import TipoFallaEnum, TipoRequerimientoEnum
from app.utils.validators import Validators


@dataclass(frozen=True)
class IncidenciaDTO:
    """Datos de entrada para registrar una Incidencia o una solicitud de apertura anticipada (RF1)."""

    descripcion: str
    id_laboratorio: int
    tipo_falla: TipoFallaEnum | None = None
    id_equipo: int | None = None
    tipo_requerimiento: TipoRequerimientoEnum = TipoRequerimientoEnum.FALLA_TECNICA
    fecha_hora_apertura: datetime | None = None
    subcategoria: str | None = None

    def __post_init__(self) -> None:
        if not Validators.es_no_vacio(self.descripcion):
            raise ValidacionException("La descripcion no puede estar vacia", campo="descripcion")
        if not Validators.es_entero_positivo(self.id_laboratorio):
            raise ValidacionException("El laboratorio es obligatorio", campo="id_laboratorio")
        if self.tipo_requerimiento == TipoRequerimientoEnum.APERTURA_ANTICIPADA:
            if self.fecha_hora_apertura is None:
                raise ValidacionException(
                    "La apertura anticipada requiere fecha y hora de inicio de clase", campo="fecha_hora_apertura"
                )
            if not Validators.es_fecha_futura(self.fecha_hora_apertura):
                raise ValidacionException(
                    "La fecha y hora de apertura anticipada debe ser futura", campo="fecha_hora_apertura"
                )
        elif self.tipo_falla is None:
            # Una apertura anticipada no tiene "tipo de falla" (no es una falla tecnica); una
            # falla tecnica si lo requiere.
            raise ValidacionException("El tipo de falla es obligatorio", campo="tipo_falla")
