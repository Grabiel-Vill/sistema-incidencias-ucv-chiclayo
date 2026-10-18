from dataclasses import dataclass

from app.exceptions import ValidacionException
from app.utils.validators import Validators


@dataclass(frozen=True)
class LaboratorioDTO:
    """Datos de alta/edicion de un Laboratorio."""

    nombre: str
    pabellon: str
    piso: int
    estado_operativo: bool = True

    def __post_init__(self) -> None:
        if not Validators.es_no_vacio(self.nombre):
            raise ValidacionException("El nombre del laboratorio no puede estar vacio", campo="nombre")
        if not Validators.es_no_vacio(self.pabellon):
            raise ValidacionException("El pabellon no puede estar vacio", campo="pabellon")
        if self.piso < 0:
            raise ValidacionException("El piso no puede ser negativo", campo="piso")
