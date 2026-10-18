from __future__ import annotations

from typing import TYPE_CHECKING

from app.exceptions import ValidacionException
from app.models.enums import EstadoIncidenciaEnum, RolEnum
from app.models.nota_tecnica import NotaTecnica
from app.models.usuario import Usuario

if TYPE_CHECKING:
    from app.models.incidencia import Incidencia

_PERMISOS_TECNICO = {"atender_incidencia", "actualizar_estado_ticket", "agregar_nota_tecnica"}


class Tecnico(Usuario):
    """Personal de soporte tecnico. Hereda de Usuario y atiende incidencias asignadas."""

    def __init__(
        self,
        id_usuario: int,
        codigo_ucv: str,
        nombre: str,
        apellido: str,
        email: str,
        password_hash: str,
        especialidad: str,
        disponible: bool = True,
        estado: bool = True,
    ):
        super().__init__(id_usuario, codigo_ucv, nombre, apellido, email, password_hash, estado)
        self.especialidad = especialidad
        self._disponible = disponible

    @property
    def especialidad(self) -> str:
        return self._especialidad

    @especialidad.setter
    def especialidad(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValidacionException("La especialidad no puede estar vacia", campo="especialidad")
        self._especialidad = valor.strip()

    @property
    def disponible(self) -> bool:
        return self._disponible

    def obtener_rol(self) -> RolEnum:
        return RolEnum.TECNICO

    def tiene_permiso(self, accion: str) -> bool:
        return accion in _PERMISOS_TECNICO

    def atender_incidencia(self, incidencia: "Incidencia") -> None:
        incidencia.asignar_tecnico(self)
        incidencia.cambiar_estado(EstadoIncidenciaEnum.EN_PROCESO)
        self._disponible = False

    def actualizar_estado_ticket(self, incidencia: "Incidencia", nuevo_estado: EstadoIncidenciaEnum) -> None:
        incidencia.cambiar_estado(nuevo_estado)
        if nuevo_estado == EstadoIncidenciaEnum.RESUELTO:
            self._disponible = True

    def agregar_nota_tecnica(self, incidencia: "Incidencia", id_nota: int, contenido: str, es_privado: bool = True) -> NotaTecnica:
        nota = NotaTecnica(id_nota=id_nota, contenido=contenido, es_privado=es_privado)
        incidencia.agregar_nota_tecnica(nota)
        return nota
