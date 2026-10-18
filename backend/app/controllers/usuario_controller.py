from typing import Callable

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dtos.usuario_dto import UsuarioDTO
from app.models.administrador import Administrador
from app.models.enums import RolEnum
from app.services.usuario_service import UsuarioService


class UsuarioSchema(BaseModel):
    codigo_ucv: str
    nombre: str
    apellido: str
    email: str
    password: str
    rol: RolEnum
    especialidad: str | None = None


class CambioEstadoSchema(BaseModel):
    activo: bool


class EdicionUsuarioSchema(BaseModel):
    codigo_ucv: str
    nombre: str
    apellido: str
    email: str
    especialidad: str | None = None


class PasswordTemporalSchema(BaseModel):
    password_temporal: str


def crear_router_usuarios(
    usuario_service: UsuarioService, requiere_administrador: Callable[..., Administrador]
) -> APIRouter:
    """Endpoints de gestion de usuarios y permisos (UC10)."""

    router = APIRouter(prefix="/usuarios", tags=["usuarios"])

    @router.post("", response_model=UsuarioDTO, status_code=201)
    def registrar_usuario(
        body: UsuarioSchema, administrador: Administrador = Depends(requiere_administrador)
    ) -> UsuarioDTO:
        return usuario_service.crear_y_registrar_usuario(
            administrador,
            rol=body.rol,
            codigo_ucv=body.codigo_ucv,
            nombre=body.nombre,
            apellido=body.apellido,
            email=body.email,
            password_plano=body.password,
            especialidad=body.especialidad,
        )

    @router.patch("/{id_usuario}/estado", response_model=UsuarioDTO)
    def cambiar_estado_usuario(
        id_usuario: int, body: CambioEstadoSchema, administrador: Administrador = Depends(requiere_administrador)
    ) -> UsuarioDTO:
        return usuario_service.cambiar_estado_usuario(administrador, id_usuario, body.activo)

    @router.put("/{id_usuario}", response_model=UsuarioDTO)
    def editar_usuario(
        id_usuario: int, body: EdicionUsuarioSchema, administrador: Administrador = Depends(requiere_administrador)
    ) -> UsuarioDTO:
        return usuario_service.editar_usuario(
            administrador,
            id_usuario,
            codigo_ucv=body.codigo_ucv,
            nombre=body.nombre,
            apellido=body.apellido,
            email=body.email,
            especialidad=body.especialidad,
        )

    @router.post("/{id_usuario}/restablecer-password", response_model=PasswordTemporalSchema)
    def restablecer_password(
        id_usuario: int, administrador: Administrador = Depends(requiere_administrador)
    ) -> PasswordTemporalSchema:
        password_temporal = usuario_service.restablecer_password(administrador, id_usuario)
        return PasswordTemporalSchema(password_temporal=password_temporal)

    @router.get("", response_model=list[UsuarioDTO])
    def listar_usuarios(administrador: Administrador = Depends(requiere_administrador)) -> list[UsuarioDTO]:
        return usuario_service.listar_usuarios(administrador)

    return router
