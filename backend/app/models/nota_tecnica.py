from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from app.exceptions import ValidacionException
from app.models.enums import RolEnum

if TYPE_CHECKING:
    from app.models.usuario import Usuario

_ROLES_CON_ACCESO_PRIVADO = {RolEnum.TECNICO, RolEnum.ADMINISTRADOR}


class NotaTecnica:
    """Nota de seguimiento dentro de una Incidencia; puede ser interna (solo soporte) o publica."""

    def __init__(self, id_nota: int, contenido: str, es_privado: bool = True, fecha_creacion: datetime | None = None):
        self._id_nota = id_nota
        self.contenido = contenido
        self._es_privado = es_privado
        self._fecha_creacion = fecha_creacion or datetime.now()
        self._id_incidencia: int | None = None

    @property
    def id_nota(self) -> int:
        return self._id_nota

    @property
    def contenido(self) -> str:
        return self._contenido

    @contenido.setter
    def contenido(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValidacionException("El contenido de la nota no puede estar vacio", campo="contenido")
        self._contenido = valor.strip()

    @property
    def es_privado(self) -> bool:
        return self._es_privado

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    def es_visible_para(self, usuario: "Usuario") -> bool:
        if not self._es_privado:
            return True
        return usuario.obtener_rol() in _ROLES_CON_ACCESO_PRIVADO

    @property
    def id_incidencia(self) -> int | None:
        return self._id_incidencia

    def asociar_incidencia(self, id_incidencia: int) -> None:
        self._id_incidencia = id_incidencia

    def __repr__(self) -> str:
        visibilidad = "privada" if self._es_privado else "publica"
        return f"NotaTecnica(id={self._id_nota}, {visibilidad})"
