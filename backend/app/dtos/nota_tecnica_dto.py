from dataclasses import dataclass

from app.exceptions import ValidacionException
from app.utils.validators import Validators


@dataclass(frozen=True)
class NotaTecnicaDTO:
    """Datos de entrada para agregar una NotaTecnica a una Incidencia."""

    contenido: str
    es_privado: bool = True

    def __post_init__(self) -> None:
        if not Validators.es_no_vacio(self.contenido):
            raise ValidacionException("El contenido de la nota no puede estar vacio", campo="contenido")
