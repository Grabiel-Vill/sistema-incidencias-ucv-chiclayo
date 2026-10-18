from dataclasses import dataclass

from app.exceptions import ValidacionException
from app.utils.validators import Validators


@dataclass(frozen=True)
class CredencialesDTO:
    """Datos de entrada para iniciar sesion con credenciales institucionales UCV."""

    email: str
    password: str

    def __post_init__(self) -> None:
        if not Validators.es_email_valido(self.email):
            raise ValidacionException("El email no tiene un formato valido", campo="email")
        if not Validators.es_no_vacio(self.password):
            raise ValidacionException("La contrasena no puede estar vacia", campo="password")
