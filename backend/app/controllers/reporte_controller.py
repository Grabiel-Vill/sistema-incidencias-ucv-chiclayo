from typing import Callable

from fastapi import APIRouter, Depends, Response

from app.models.administrador import Administrador
from app.models.enums import FormatoEnum
from app.repositories.reporte_repository import ReporteRepository
from app.services.reporte_service import ReporteService

_MEDIA_TYPES = {
    FormatoEnum.PDF: "application/pdf",
    FormatoEnum.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
_EXTENSIONES = {FormatoEnum.PDF: "pdf", FormatoEnum.EXCEL: "xlsx"}


def crear_router_reportes(
    reporte_service: ReporteService,
    reporte_repository: ReporteRepository,
    requiere_administrador: Callable[..., Administrador],
) -> APIRouter:
    """Endpoints de generacion e historial de reportes de mantenimiento (RF5, UC12)."""

    router = APIRouter(prefix="/reportes", tags=["reportes"])

    @router.post("", status_code=201)
    def generar_reporte(administrador: Administrador = Depends(requiere_administrador)):
        reporte = reporte_service.generar_reporte(administrador)
        return _a_respuesta(reporte)

    @router.get("")
    def listar_historial(limite: int = 10, _: Administrador = Depends(requiere_administrador)):
        return [_a_respuesta(r) for r in reporte_repository.listar_mas_recientes(limite)]

    @router.get("/{id_reporte}/exportar")
    def exportar_reporte(
        id_reporte: int, formato: FormatoEnum = FormatoEnum.PDF, _: Administrador = Depends(requiere_administrador)
    ) -> Response:
        reporte = reporte_repository.obtener_por_id(id_reporte)
        contenido = reporte_service.exportar(reporte, formato)
        nombre_archivo = f"reporte-{id_reporte}.{_EXTENSIONES[formato]}"
        return Response(
            content=contenido,
            media_type=_MEDIA_TYPES[formato],
            headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
        )

    return router


def _a_respuesta(reporte) -> dict:
    return {
        "id_reporte": reporte.id_reporte,
        "fecha_generacion": reporte.fecha_generacion,
        "kpis_laboratorios": reporte.kpis_laboratorios,
        "frecuencia_fallas": reporte.frecuencia_fallas,
    }
