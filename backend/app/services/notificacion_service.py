from app.integrations.email_client import EmailClient
from app.models.enums import TipoNotificacionEnum
from app.models.incidencia import Incidencia
from app.models.notificacion import Notificacion
from app.models.usuario import Usuario
from app.repositories.notificacion_repository import NotificacionRepository


class NotificacionService:
    """Crea y envia notificaciones de asignacion/cambio de estado (RF2, RF4)."""

    def __init__(self, notificacion_repository: NotificacionRepository, email_client: EmailClient | None = None):
        self._notificaciones = notificacion_repository
        self._email_client = email_client

    def notificar_asignacion(self, usuario: Usuario, incidencia: Incidencia) -> Notificacion:
        mensaje = f"Se te asigno el ticket {incidencia.codigo_ticket}: {incidencia.descripcion}"
        return self._crear_y_enviar(usuario, mensaje, TipoNotificacionEnum.ASIGNACION, prioridad=incidencia.prioridad)

    def notificar_tecnico_asignado_a_docente(self, docente: Usuario, incidencia: Incidencia, tecnico: Usuario) -> Notificacion:
        mensaje = f"Tu ticket {incidencia.codigo_ticket} fue asignado al tecnico {tecnico.nombre_completo}"
        return self._crear_y_enviar(docente, mensaje, TipoNotificacionEnum.ASIGNACION)

    def notificar_cambio_estado(self, usuario: Usuario, incidencia: Incidencia) -> Notificacion:
        mensaje = f"El ticket {incidencia.codigo_ticket} cambio de estado a {incidencia.estado.value}"
        return self._crear_y_enviar(usuario, mensaje, TipoNotificacionEnum.CAMBIO_ESTADO)

    def _crear_y_enviar(
        self, usuario: Usuario, mensaje: str, tipo: TipoNotificacionEnum, prioridad=None
    ) -> Notificacion:
        notificacion = Notificacion(
            id_notificacion=self._notificaciones.siguiente_id(), mensaje=mensaje, tipo=tipo, prioridad=prioridad
        )
        notificacion.enviar_notificacion(usuario)
        self._notificaciones.agregar(notificacion)
        if self._email_client is not None:
            self._email_client.enviar(usuario.email, "Sistema de Incidencias UCV", mensaje)
        return notificacion
