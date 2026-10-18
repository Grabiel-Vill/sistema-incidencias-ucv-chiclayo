from app.dtos.metricas_dto import MetricasDTO
from app.models.administrador import Administrador
from app.models.enums import FormatoEnum
from app.repositories.calificacion_repository import CalificacionRepository
from app.services.reporte_service import ReporteService


class DashboardService:
    """Fachada de metricas para el panel administrativo (RF5); reutiliza ReporteService
    en vez de recalcular KPIs/frecuencia de fallas por su cuenta."""

    def __init__(self, reporte_service: ReporteService, calificacion_repository: CalificacionRepository | None = None):
        self._reporte_service = reporte_service
        self._calificaciones = calificacion_repository

    def obtener_metricas(self, administrador: Administrador) -> MetricasDTO:
        reporte = self._reporte_service.generar_reporte(administrador)
        evaluacion_promedio = self._calificaciones.promedio_estrellas() if self._calificaciones is not None else None
        return MetricasDTO.desde_reporte(reporte, evaluacion_promedio_tecnicos=evaluacion_promedio)

    def exportar_reporte(self, administrador: Administrador, formato: FormatoEnum) -> bytes:
        reporte = self._reporte_service.generar_reporte(administrador)
        return self._reporte_service.exportar(reporte, formato)
