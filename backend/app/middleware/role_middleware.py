from typing import Callable

from fastapi import Depends

from app.exceptions import AccesoDenegadoException
from app.models.enums import RolEnum
from app.models.usuario import Usuario


def crear_dependencia_rol(obtener_usuario_actual: Callable[..., Usuario], *roles_permitidos: RolEnum) -> Callable[..., Usuario]:
    """Encadena sobre obtener_usuario_actual y exige uno de los roles indicados (RNF4, control de acceso)."""

    def verificar_rol(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
        if usuario.obtener_rol() not in roles_permitidos:
            nombres = ", ".join(rol.value for rol in roles_permitidos)
            raise AccesoDenegadoException(f"Esta accion requiere el rol: {nombres}")
        return usuario

    return verificar_rol
