from __future__ import annotations

from app.models.enums import RolEnum
from app.models.incidencia import Incidencia
from app.models.laboratorio import Laboratorio
from app.models.reporte import Reporte
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario

_PERMISOS_ADMINISTRADOR = {
    "gestionar_usuario",
    "gestionar_laboratorio",
    "asignar_responsable_incidencia",
    "generar_reporte_mantenimiento",
}


class Administrador(Usuario):
    """Autoridad UCV con permisos de gestion de usuarios, laboratorios y reportes (RF5)."""

    def obtener_rol(self) -> RolEnum:
        return RolEnum.ADMINISTRADOR

    def tiene_permiso(self, accion: str) -> bool:
        return accion in _PERMISOS_ADMINISTRADOR

    def gestionar_usuario(self, usuario: Usuario, activo: bool) -> None:
        usuario.activar() if activo else usuario.desactivar()

    def gestionar_laboratorio(
        self,
        laboratorio: Laboratorio,
        nombre: str | None = None,
        pabellon: str | None = None,
        piso: int | None = None,
        estado_operativo: bool | None = None,
    ) -> None:
        if nombre is not None:
            laboratorio.nombre = nombre
        if pabellon is not None:
            laboratorio.pabellon = pabellon
        if piso is not None:
            laboratorio.piso = piso
        if estado_operativo is not None:
            laboratorio.actualizar_estado_operativo(estado_operativo)

    def asignar_responsable_incidencia(self, incidencia: Incidencia, tecnico: Tecnico) -> None:
        incidencia.asignar_tecnico(tecnico)

    def generar_reporte_mantenimiento(self, id_reporte: int, incidencias: list[Incidencia]) -> Reporte:
        reporte = Reporte(id_reporte=id_reporte)
        reporte.obtener_kpis_laboratorios(incidencias)
        reporte.obtener_frecuencia_fallas(incidencias)
        reporte.obtener_puntualidad_apertura(incidencias)
        return reporte
