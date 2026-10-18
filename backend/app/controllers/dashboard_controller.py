from typing import Callable

from fastapi import APIRouter, Depends, Response

from app.dtos.metricas_dto import MetricasDTO
from app.models.administrador import Administrador
from app.models.enums import FormatoEnum
from app.services.dashboard_service import DashboardService

_MEDIA_TYPES = {
    FormatoEnum.PDF: "application/pdf",
    FormatoEnum.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
_EXTENSIONES = {FormatoEnum.PDF: "pdf", FormatoEnum.EXCEL: "xlsx"}


def crear_router_dashboard(
    dashboard_service: DashboardService, requiere_administrador: Callable[..., Administrador]
) -> APIRouter:
    """Endpoints del panel de control administrativo (RF5, UC09)."""

    router = APIRouter(prefix="/dashboard", tags=["dashboard"])

    @router.get("/metricas", response_model=MetricasDTO)
    def obtener_metricas(administrador: Administrador = Depends(requiere_administrador)) -> MetricasDTO:
        return dashboard_service.obtener_metricas(administrador)

    @router.get("/reporte")
    def exportar_reporte(
        formato: FormatoEnum = FormatoEnum.PDF, administrador: Administrador = Depends(requiere_administrador)
    ) -> Response:
        contenido = dashboard_service.exportar_reporte(administrador, formato)
        nombre_archivo = f"reporte-mantenimiento.{_EXTENSIONES[formato]}"
        return Response(
            content=contenido,
            media_type=_MEDIA_TYPES[formato],
            headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
        )

    return router
