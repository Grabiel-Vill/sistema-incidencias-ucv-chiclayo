from app.exceptions.app_exception import AppException


class CredencialesInvalidasException(AppException):
    """Se lanza cuando el codigo UCV/email o la contrasena no coinciden durante el login."""

    def __init__(self, mensaje: str = "Credenciales invalidas"):
        super().__init__(mensaje, codigo="CREDENCIALES_INVALIDAS")
