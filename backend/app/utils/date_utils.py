from datetime import datetime, timedelta


class DateUtils:
    """Utilidades de fecha/hora compartidas por services, dtos y exporters."""

    @staticmethod
    def ahora() -> datetime:
        return datetime.now()

    @staticmethod
    def formatear_iso(fecha: datetime | None) -> str | None:
        return fecha.isoformat() if fecha else None

    @staticmethod
    def formatear_legible(fecha: datetime | None) -> str:
        if fecha is None:
            return "-"
        return fecha.strftime("%d/%m/%Y %H:%M")

    @staticmethod
    def calcular_duracion_minutos(inicio: datetime | None, fin: datetime | None) -> float | None:
        if inicio is None or fin is None:
            return None
        return round((fin - inicio).total_seconds() / 60, 2)

    @staticmethod
    def formatear_duracion(duracion: timedelta | None) -> str:
        if duracion is None:
            return "-"
        total_minutos = int(duracion.total_seconds() // 60)
        horas, minutos = divmod(total_minutos, 60)
        return f"{horas}h {minutos}m"

    @staticmethod
    def esta_en_rango(fecha: datetime, desde: datetime | None, hasta: datetime | None) -> bool:
        if desde and fecha < desde:
            return False
        if hasta and fecha > hasta:
            return False
        return True
