from app.exceptions.app_exception import AppException


class TransicionEstadoInvalidaException(AppException):
    """Se lanza cuando se intenta cambiar el estado de una Incidencia/Equipo a un estado no permitido."""

    def __init__(self, estado_actual: object, estado_destino: object):
        actual = getattr(estado_actual, "value", estado_actual)
        destino = getattr(estado_destino, "value", estado_destino)
        super().__init__(
            f"No se puede pasar de '{actual}' a '{destino}'",
            codigo="TRANSICION_ESTADO_INVALIDA",
        )
        self.estado_actual = estado_actual
        self.estado_destino = estado_destino
