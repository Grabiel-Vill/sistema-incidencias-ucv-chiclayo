from dataclasses import dataclass

from app.exceptions import ValidacionException
from app.models.enums import EstadoEquipoEnum
from app.utils.validators import Validators


@dataclass(frozen=True)
class EquipoDTO:
    """Datos de alta/edicion de un Equipo de laboratorio."""

    codigo_patrimonial: str
    tipo_equipo: str
    estado: EstadoEquipoEnum = EstadoEquipoEnum.OPERATIVO

    def __post_init__(self) -> None:
        if not Validators.es_no_vacio(self.codigo_patrimonial):
            raise ValidacionException("El codigo patrimonial no puede estar vacio", campo="codigo_patrimonial")
        if not Validators.es_no_vacio(self.tipo_equipo):
            raise ValidacionException("El tipo de equipo no puede estar vacio", campo="tipo_equipo")
