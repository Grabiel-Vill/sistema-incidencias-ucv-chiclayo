from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.models.enums import TipoFallaEnum

if TYPE_CHECKING:
    from app.models.reporte import Reporte


@dataclass(frozen=True)
class MetricasDTO:
    """Indicadores del dashboard administrativo: KPIs por laboratorio y frecuencia de fallas (RF5)."""

    kpis_laboratorios: dict[int, dict] = field(default_factory=dict)
    frecuencia_fallas: dict[TipoFallaEnum, int] = field(default_factory=dict)
    equipos_criticos: list[str] = field(default_factory=list)
    puntualidad_apertura: float | None = None
    evaluacion_promedio_tecnicos: float | None = None

    @classmethod
    def desde_reporte(
        cls,
        reporte: "Reporte",
        equipos_criticos: list[str] | None = None,
        evaluacion_promedio_tecnicos: float | None = None,
    ) -> "MetricasDTO":
        return cls(
            kpis_laboratorios=reporte.kpis_laboratorios,
            frecuencia_fallas=reporte.frecuencia_fallas,
            equipos_criticos=equipos_criticos or [],
            puntualidad_apertura=reporte.puntualidad_apertura,
            evaluacion_promedio_tecnicos=evaluacion_promedio_tecnicos,
        )
