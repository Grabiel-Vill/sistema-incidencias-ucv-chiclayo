from dataclasses import dataclass


@dataclass(frozen=True)
class TokenDTO:
    """Token de sesion devuelto tras un inicio de sesion exitoso."""

    access_token: str
    rol: str
    expiracion: str
    tipo: str = "Bearer"
