from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.usuario import Usuario


@dataclass(frozen=True)
class UsuarioDTO:
    """Datos publicos de un Usuario, sin password_hash, listos para ser serializados."""

    id_usuario: int
    codigo_ucv: str
    nombre: str
    apellido: str
    email: str
    rol: str
    estado: bool
    especialidad: str | None = None

    @classmethod
    def desde_usuario(cls, usuario: "Usuario") -> "UsuarioDTO":
        return cls(
            id_usuario=usuario.id_usuario,
            codigo_ucv=usuario.codigo_ucv,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            email=usuario.email,
            rol=usuario.obtener_rol().value,
            estado=usuario.estado,
            especialidad=getattr(usuario, "especialidad", None),
        )
