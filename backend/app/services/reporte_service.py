from app.exceptions import AccesoDenegadoException
from app.models.administrador import Administrador
from app.models.enums import FormatoEnum
from app.models.reporte import Reporte
from app.repositories.incidencia_repository import IncidenciaRepository
from app.repositories.reporte_repository import ReporteRepository
from app.utils.excel_exporter import ExcelExporter
from app.utils.pdf_exporter import PdfExporter

_EXPORTADORES = {
    FormatoEnum.PDF: PdfExporter.exportar,
    FormatoEnum.EXCEL: ExcelExporter.exportar,
}


class ReporteService:
    """Genera y exporta reportes de mantenimiento con KPIs e historial de fallas (RF5)."""

    def __init__(self, reporte_repository: ReporteRepository, incidencia_repository: IncidenciaRepository):
        self._reportes = reporte_repository
        self._incidencias = incidencia_repository

    def generar_reporte(self, administrador: Administrador) -> Reporte:
        if not administrador.tiene_permiso("generar_reporte_mantenimiento"):
            raise AccesoDenegadoException("El usuario no tiene permiso para generar reportes")
        reporte = administrador.generar_reporte_mantenimiento(
            id_reporte=self._reportes.siguiente_id(), incidencias=self._incidencias.listar()
        )
        self._reportes.agregar(reporte)
        return reporte

    def exportar(self, reporte: Reporte, formato: FormatoEnum) -> bytes:
        return _EXPORTADORES[formato](reporte)
