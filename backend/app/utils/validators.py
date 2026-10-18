import re
from datetime import datetime

_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Validators:
    """Validaciones reutilizables, sin estado, para usarse en controllers/services al parsear entrada."""

    @staticmethod
    def es_email_valido(email: str) -> bool:
        return bool(email) and bool(_EMAIL_REGEX.match(email.strip()))

    @staticmethod
    def es_fecha_futura(fecha: datetime | None) -> bool:
        if fecha is None:
            return False
        ahora = datetime.now(fecha.tzinfo) if fecha.tzinfo is not None else datetime.now()
        return fecha > ahora

    @staticmethod
    def es_no_vacio(valor: str | None) -> bool:
        return bool(valor) and bool(valor.strip())

    @staticmethod
    def es_entero_positivo(valor: int) -> bool:
        return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0

    @staticmethod
    def tiene_extension_valida(nombre_archivo: str, extensiones_permitidas: tuple[str, ...]) -> bool:
        if not Validators.es_no_vacio(nombre_archivo):
            return False
        return nombre_archivo.lower().endswith(tuple(ext.lower() for ext in extensiones_permitidas))
