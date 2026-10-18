class AppException(Exception):
    """Excepcion base de dominio: toda excepcion propia del sistema hereda de esta clase."""

    def __init__(self, mensaje: str, codigo: str | None = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo or self.__class__.__name__

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.mensaje}"
