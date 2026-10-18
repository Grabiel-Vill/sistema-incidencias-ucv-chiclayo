from app.exceptions.app_exception import AppException


class RecursoNoEncontradoException(AppException):
    """Se lanza cuando se busca una entidad (Incidencia, Usuario, Laboratorio, etc.) que no existe."""

    def __init__(self, recurso: str, identificador: object):
        super().__init__(
            f"{recurso} con identificador '{identificador}' no fue encontrado",
            codigo="RECURSO_NO_ENCONTRADO",
        )
        self.recurso = recurso
        self.identificador = identificador
