from enum import Enum


class TipoNotificacionEnum(str, Enum):
    """Origen/motivo de una Notificacion enviada a un Usuario."""

    ASIGNACION = "ASIGNACION"
    CAMBIO_ESTADO = "CAMBIO_ESTADO"
