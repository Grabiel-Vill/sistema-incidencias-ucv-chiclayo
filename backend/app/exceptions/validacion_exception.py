from app.exceptions.app_exception import AppException


class ValidacionException(AppException):
    """Se lanza cuando un dato de entrada no cumple las reglas de un campo del dominio."""

    def __init__(self, mensaje: str, campo: str | None = None):
        super().__init__(mensaje, codigo="VALIDACION")
        self.campo = campo

    def __str__(self) -> str:
        if self.campo:
            return f"[{self.codigo}] {self.campo}: {self.mensaje}"
        return super().__str__()
