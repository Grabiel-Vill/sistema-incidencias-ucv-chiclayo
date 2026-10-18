from __future__ import annotations

from datetime import datetime

from app.models.enums import EstadoIncidenciaEnum, TipoFallaEnum, TipoRequerimientoEnum
from app.models.incidencia import Incidencia


class Reporte:
    """Calcula metricas e indicadores (KPIs) a partir de un conjunto de Incidencia ya cargado (RF5)."""

    def __init__(self, id_reporte: int, fecha_generacion: datetime | None = None):
        self._id_reporte = id_reporte
        self._fecha_generacion = fecha_generacion or datetime.now()
        self._kpis_laboratorios: dict[int, dict] = {}
        self._frecuencia_fallas: dict[TipoFallaEnum, int] = {}
        self._puntualidad_apertura: float | None = None

    @property
    def id_reporte(self) -> int:
        return self._id_reporte

    @property
    def fecha_generacion(self) -> datetime:
        return self._fecha_generacion

    @property
    def kpis_laboratorios(self) -> dict[int, dict]:
        return dict(self._kpis_laboratorios)

    @property
    def frecuencia_fallas(self) -> dict[TipoFallaEnum, int]:
        return dict(self._frecuencia_fallas)

    @property
    def puntualidad_apertura(self) -> float | None:
        return self._puntualidad_apertura

    def obtener_kpis_laboratorios(self, incidencias: list[Incidencia]) -> dict[int, dict]:
        kpis: dict[int, dict] = {}
        for incidencia in incidencias:
            laboratorio_id = incidencia.laboratorio.id_laboratorio
            resumen = kpis.setdefault(
                laboratorio_id,
                {
                    "laboratorio": incidencia.laboratorio.nombre,
                    "total_incidencias": 0,
                    "resueltas": 0,
                    "suma_minutos_atencion": 0.0,
                    "incidencias_con_atencion": 0,
                },
            )
            resumen["total_incidencias"] += 1
            if incidencia.estado == EstadoIncidenciaEnum.RESUELTO:
                resumen["resueltas"] += 1
            tiempo_atencion = incidencia.calcular_tiempo_atencion()
            if tiempo_atencion is not None:
                resumen["suma_minutos_atencion"] += tiempo_atencion.total_seconds() / 60
                resumen["incidencias_con_atencion"] += 1

        for resumen in kpis.values():
            atendidas = resumen.pop("incidencias_con_atencion")
            suma_minutos = resumen.pop("suma_minutos_atencion")
            resumen["tiempo_promedio_atencion_minutos"] = round(suma_minutos / atendidas, 2) if atendidas else None

        self._kpis_laboratorios = kpis
        return kpis

    def obtener_frecuencia_fallas(self, incidencias: list[Incidencia]) -> dict[TipoFallaEnum, int]:
        frecuencia: dict[TipoFallaEnum, int] = {tipo: 0 for tipo in TipoFallaEnum}
        for incidencia in incidencias:
            # Una apertura anticipada no tiene tipo_falla (no es una falla tecnica): no cuenta
            # para este indicador, que mide frecuencia de FALLAS.
            if incidencia.tipo_falla is not None:
                frecuencia[incidencia.tipo_falla] += 1
        self._frecuencia_fallas = frecuencia
        return frecuencia

    def obtener_puntualidad_apertura(self, incidencias: list[Incidencia]) -> float | None:
        """% de solicitudes de apertura anticipada ya RESUELTAS cuya fecha_resolucion llego a
        tiempo (antes o igual a la fecha_hora_apertura solicitada). None si no hay ninguna
        resuelta todavia (no hay base de calculo)."""
        resueltas = [
            i
            for i in incidencias
            if i.tipo_requerimiento == TipoRequerimientoEnum.APERTURA_ANTICIPADA
            and i.estado == EstadoIncidenciaEnum.RESUELTO
            and i.fecha_hora_apertura is not None
            and i.fecha_resolucion is not None
        ]
        if not resueltas:
            self._puntualidad_apertura = None
            return None
        a_tiempo = sum(1 for i in resueltas if i.fecha_resolucion <= i.fecha_hora_apertura)
        self._puntualidad_apertura = round(a_tiempo / len(resueltas) * 100, 2)
        return self._puntualidad_apertura

    def __repr__(self) -> str:
        return f"Reporte(id={self._id_reporte}, fecha_generacion={self._fecha_generacion.isoformat()})"
