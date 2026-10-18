class TicketCodeGenerator:
    """Genera el codigo unico de ticket visible para el usuario (RF1)."""

    @staticmethod
    def generar(id_incidencia: int, prefijo: str = "INC") -> str:
        return f"{prefijo}-{id_incidencia:06d}"
