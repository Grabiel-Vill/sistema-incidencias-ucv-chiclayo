from app.exceptions.app_exception import AppException


class AccesoDenegadoException(AppException):
    """Se lanza cuando un Usuario intenta una accion para la que su rol no tiene permiso."""

    def __init__(self, mensaje: str = "Acceso denegado"):
        super().__init__(mensaje, codigo="ACCESO_DENEGADO")
