from io import BytesIO

from openpyxl import Workbook

from app.models.reporte import Reporte


class ExcelExporter:
    """Serializa un Reporte ya calculado (KPIs + frecuencia de fallas) a un archivo .xlsx real (RF5)."""

    @staticmethod
    def exportar(reporte: Reporte) -> bytes:
        libro = Workbook()

        hoja_kpis = libro.active
        hoja_kpis.title = "KPIs por laboratorio"
        hoja_kpis.append(["Laboratorio", "Total incidencias", "Resueltas", "Tiempo promedio atencion (min)"])
        for datos in reporte.kpis_laboratorios.values():
            hoja_kpis.append(
                [
                    datos["laboratorio"],
                    datos["total_incidencias"],
                    datos["resueltas"],
                    datos["tiempo_promedio_atencion_minutos"],
                ]
            )

        hoja_fallas = libro.create_sheet("Frecuencia de fallas")
        hoja_fallas.append(["Tipo de falla", "Cantidad"])
        for tipo_falla, cantidad in reporte.frecuencia_fallas.items():
            hoja_fallas.append([tipo_falla.value, cantidad])

        buffer = BytesIO()
        libro.save(buffer)
        return buffer.getvalue()
