from typing import Callable

from fastapi import APIRouter, Depends

from app.exceptions import RecursoNoEncontradoException
from app.models.usuario import Usuario
from app.repositories.notificacion_repository import NotificacionRepository


def crear_router_notificaciones(
    notificacion_repository: NotificacionRepository, obtener_usuario_actual: Callable[..., Usuario]
) -> APIRouter:
    """Endpoints para que un Usuario consulte y marque como leidas sus notificaciones (RF2, UC08)."""

    router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])

    @router.get("")
    def listar_notificaciones(solo_no_leidas: bool = False, usuario: Usuario = Depends(obtener_usuario_actual)):
        notificaciones = notificacion_repository.listar_por_usuario(usuario.id_usuario, solo_no_leidas=solo_no_leidas)
        return [_a_respuesta(n) for n in notificaciones]

    @router.patch("/{id_notificacion}/leido")
    def marcar_leido(id_notificacion: int, usuario: Usuario = Depends(obtener_usuario_actual)):
        notificacion = next(
            (n for n in notificacion_repository.listar_por_usuario(usuario.id_usuario) if n.id_notificacion == id_notificacion),
            None,
        )
        if notificacion is None:
            raise RecursoNoEncontradoException("Notificacion", id_notificacion)
        notificacion.marcar_leido()
        notificacion_repository.actualizar(notificacion)
        return _a_respuesta(notificacion)

    return router


def _a_respuesta(notificacion) -> dict:
    return {
        "id_notificacion": notificacion.id_notificacion,
        "mensaje": notificacion.mensaje,
        "tipo": notificacion.tipo,
        "fecha": notificacion.fecha,
        "leido": notificacion.leido,
        "prioridad": notificacion.prioridad,
    }
