from typing import Callable

from fastapi import Header

from app.exceptions import CredencialesInvalidasException
from app.models.usuario import Usuario
from app.services.auth_service import AuthService


def crear_dependencia_usuario_actual(auth_service: AuthService) -> Callable[..., Usuario]:
    """Crea una dependencia de FastAPI que extrae y valida el Bearer token de la peticion (RNF4)."""

    def obtener_usuario_actual(authorization: str | None = Header(default=None)) -> Usuario:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise CredencialesInvalidasException("Falta el header Authorization: Bearer <token>")
        token = authorization.split(" ", 1)[1]
        return auth_service.obtener_usuario_autenticado(token)

    return obtener_usuario_actual
