from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from app.exceptions import ValidacionException
from app.models.enums import PrioridadEnum, TipoNotificacionEnum

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Notificacion:
    """Notificacion del sistema (asignacion de ticket, cambio de estado, etc.)."""

    def __init__(
        self,
        id_notificacion: int,
        mensaje: str,
        tipo: TipoNotificacionEnum,
        fecha: datetime | None = None,
        leido: bool = False,
        id_usuario: int | None = None,
        prioridad: PrioridadEnum | None = None,
    ):
        self._id_notificacion = id_notificacion
        self.mensaje = mensaje
        self._tipo = tipo
        self._fecha = fecha or datetime.now()
        self._leido = leido
        self._id_usuario = id_usuario
        self._prioridad = prioridad

    @property
    def id_notificacion(self) -> int:
        return self._id_notificacion

    @property
    def mensaje(self) -> str:
        return self._mensaje

    @mensaje.setter
    def mensaje(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValidacionException("El mensaje de la notificacion no puede estar vacio", campo="mensaje")
        self._mensaje = valor.strip()

    @property
    def tipo(self) -> TipoNotificacionEnum:
        return self._tipo

    @property
    def fecha(self) -> datetime:
        return self._fecha

    @property
    def leido(self) -> bool:
        return self._leido

    @property
    def id_usuario(self) -> int | None:
        return self._id_usuario

    @property
    def prioridad(self) -> PrioridadEnum | None:
        return self._prioridad

    def marcar_leido(self) -> None:
        self._leido = True

    def enviar_notificacion(self, usuario: "Usuario") -> None:
        self._id_usuario = usuario.id_usuario
        usuario.recibir_notificacion(self)

    def __repr__(self) -> str:
        return f"Notificacion(id={self._id_notificacion}, tipo={self._tipo.value}, leido={self._leido})"
