from __future__ import annotations

from datetime import datetime

from app.models.enums import EstadoIncidenciaEnum, RolEnum, TipoFallaEnum, TipoRequerimientoEnum
from app.models.equipo import Equipo
from app.models.incidencia import Incidencia
from app.models.laboratorio import Laboratorio
from app.models.usuario import Usuario

_PERMISOS_DOCENTE = {"crear_incidencia", "consultar_estado_incidencia"}


class Docente(Usuario):
    """Usuario que reporta incidencias y solicitudes de apertura anticipada (RF1, RF2)."""

    def obtener_rol(self) -> RolEnum:
        return RolEnum.DOCENTE

    def tiene_permiso(self, accion: str) -> bool:
        return accion in _PERMISOS_DOCENTE

    def crear_incidencia(
        self,
        id_incidencia: int,
        descripcion: str,
        tipo_falla: TipoFallaEnum | None,
        laboratorio: Laboratorio,
        tipo_requerimiento: TipoRequerimientoEnum = TipoRequerimientoEnum.FALLA_TECNICA,
        equipo: Equipo | None = None,
        fecha_hora_apertura: datetime | None = None,
        subcategoria: str | None = None,
    ) -> Incidencia:
        return Incidencia.crear(
            id_incidencia=id_incidencia,
            descripcion=descripcion,
            tipo_falla=tipo_falla,
            laboratorio=laboratorio,
            docente=self,
            tipo_requerimiento=tipo_requerimiento,
            equipo=equipo,
            fecha_hora_apertura=fecha_hora_apertura,
            subcategoria=subcategoria,
        )

    def consultar_estado_incidencia(self, incidencia: Incidencia) -> EstadoIncidenciaEnum:
        return incidencia.estado
