from typing import Callable

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dtos.credenciales_dto import CredencialesDTO
from app.dtos.token_dto import TokenDTO
from app.dtos.usuario_dto import UsuarioDTO
from app.models.usuario import Usuario
from app.services.auth_service import AuthService


class CredencialesSchema(BaseModel):
    email: str
    password: str


def crear_router_auth(auth_service: AuthService, obtener_usuario_actual: Callable[..., Usuario]) -> APIRouter:
    """Endpoints del modulo de autenticacion (UC13)."""

    router = APIRouter(prefix="/auth", tags=["auth"])

    @router.post("/login", response_model=TokenDTO)
    def iniciar_sesion(body: CredencialesSchema) -> TokenDTO:
        return auth_service.iniciar_sesion(CredencialesDTO(email=body.email, password=body.password))

    @router.post("/logout", status_code=204)
    def cerrar_sesion(usuario: Usuario = Depends(obtener_usuario_actual)) -> None:
        auth_service.cerrar_sesion(usuario)

    @router.get("/me", response_model=UsuarioDTO)
    def obtener_perfil(usuario: Usuario = Depends(obtener_usuario_actual)) -> UsuarioDTO:
        return UsuarioDTO.desde_usuario(usuario)

    return router
