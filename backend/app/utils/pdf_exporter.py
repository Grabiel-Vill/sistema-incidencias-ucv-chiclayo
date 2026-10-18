from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.reporte import Reporte

_ESTILO_TABLA = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
    ]
)


class PdfExporter:
    """Serializa un Reporte ya calculado (KPIs + frecuencia de fallas) a un archivo .pdf real (RF5)."""

    @staticmethod
    def exportar(reporte: Reporte) -> bytes:
        buffer = BytesIO()
        documento = SimpleDocTemplate(buffer, pagesize=A4, title=f"Reporte {reporte.id_reporte}")
        estilos = getSampleStyleSheet()
        elementos = [
            Paragraph(f"Reporte de mantenimiento N° {reporte.id_reporte}", estilos["Title"]),
            Paragraph(f"Generado el {reporte.fecha_generacion.strftime('%d/%m/%Y %H:%M')}", estilos["Normal"]),
            Spacer(1, 16),
            Paragraph("KPIs por laboratorio", estilos["Heading2"]),
        ]

        filas_kpis = [["Laboratorio", "Total", "Resueltas", "Tiempo prom. atencion (min)"]]
        for datos in reporte.kpis_laboratorios.values():
            filas_kpis.append(
                [
                    datos["laboratorio"],
                    str(datos["total_incidencias"]),
                    str(datos["resueltas"]),
                    str(datos["tiempo_promedio_atencion_minutos"] or "-"),
                ]
            )
        tabla_kpis = Table(filas_kpis, hAlign="LEFT")
        tabla_kpis.setStyle(_ESTILO_TABLA)
        elementos.append(tabla_kpis)
        elementos.append(Spacer(1, 24))

        elementos.append(Paragraph("Frecuencia de fallas", estilos["Heading2"]))
        filas_fallas = [["Tipo de falla", "Cantidad"]]
        for tipo_falla, cantidad in reporte.frecuencia_fallas.items():
            filas_fallas.append([tipo_falla.value, str(cantidad)])
        tabla_fallas = Table(filas_fallas, hAlign="LEFT")
        tabla_fallas.setStyle(_ESTILO_TABLA)
        elementos.append(tabla_fallas)

        documento.build(elementos)
        return buffer.getvalue()
