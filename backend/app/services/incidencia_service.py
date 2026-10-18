from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import TYPE_CHECKING

from app.dtos.filtro_dto import FiltroDTO
from app.dtos.incidencia_dto import IncidenciaDTO
from app.dtos.incidencia_respuesta_dto import IncidenciaRespuestaDTO
from app.exceptions import AccesoDenegadoException, ValidacionException
from app.models.administrador import Administrador
from app.models.docente import Docente
from app.models.enums import EstadoIncidenciaEnum, PrioridadEnum
from app.models.tecnico import Tecnico
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.equipo_repository import EquipoRepository
from app.repositories.incidencia_repository import IncidenciaRepository
from app.repositories.laboratorio_repository import LaboratorioRepository
from app.repositories.nota_tecnica_repository import NotaTecnicaRepository

if TYPE_CHECKING:
    from app.services.notificacion_service import NotificacionService


class IncidenciaService:
    """Registra, consulta, asigna, prioriza y cambia el estado de una Incidencia (RF1, RF2, RF4)."""

    def __init__(
        self,
        incidencia_repository: IncidenciaRepository,
        laboratorio_repository: LaboratorioRepository,
        equipo_repository: EquipoRepository,
        notificacion_service: "NotificacionService | None" = None,
        nota_tecnica_repository: NotaTecnicaRepository | None = None,
        calificacion_repository: CalificacionRepository | None = None,
    ):
        self._incidencias = incidencia_repository
        self._laboratorios = laboratorio_repository
        self._equipos = equipo_repository
        self._notificaciones = notificacion_service
        self._notas_tecnicas = nota_tecnica_repository
        self._calificaciones = calificacion_repository

    def registrar_incidencia(
        self, docente: Docente, datos: IncidenciaDTO, prioridad: PrioridadEnum | None = None
    ) -> IncidenciaRespuestaDTO:
        laboratorio = self._laboratorios.obtener_por_id(datos.id_laboratorio)
        if not laboratorio.estado_operativo:
            raise ValidacionException(
                "El laboratorio esta en mantenimiento y no admite nuevos tickets", campo="id_laboratorio"
            )
        equipo = self._equipos.obtener_por_id(datos.id_equipo) if datos.id_equipo is not None else None

        incidencia = docente.crear_incidencia(
            id_incidencia=self._incidencias.siguiente_id(),
            descripcion=datos.descripcion,
            tipo_falla=datos.tipo_falla,
            laboratorio=laboratorio,
            tipo_requerimiento=datos.tipo_requerimiento,
            equipo=equipo,
            fecha_hora_apertura=datos.fecha_hora_apertura,
            subcategoria=datos.subcategoria,
        )
        if prioridad is not None:
            incidencia.prioridad = prioridad
        self._incidencias.agregar(incidencia)
        return IncidenciaRespuestaDTO.desde_incidencia(incidencia)

    def consultar_estado(self, docente: Docente, id_incidencia: int) -> IncidenciaRespuestaDTO:
        incidencia = self._incidencias.obtener_por_id(id_incidencia)
        docente.consultar_estado_incidencia(incidencia)
        return IncidenciaRespuestaDTO.desde_incidencia(incidencia)

    def obtener_por_id(self, id_incidencia: int) -> IncidenciaRespuestaDTO:
        return IncidenciaRespuestaDTO.desde_incidencia(self._incidencias.obtener_por_id(id_incidencia))

    def listar_con_filtro(self, filtro: FiltroDTO) -> list[IncidenciaRespuestaDTO]:
        return [IncidenciaRespuestaDTO.desde_incidencia(i) for i in self._incidencias.listar_con_filtro(filtro)]

    def listar_mias(self, docente: Docente) -> list[IncidenciaRespuestaDTO]:
        resultado = []
        for incidencia in self._incidencias.listar_por_docente(docente.id_usuario):
            dto = IncidenciaRespuestaDTO.desde_incidencia(incidencia)
            if self._calificaciones is not None and incidencia.estado == EstadoIncidenciaEnum.RESUELTO:
                calificada = self._calificaciones.buscar_por_incidencia(incidencia.id_incidencia) is not None
                dto = replace(dto, calificada=calificada)
            resultado.append(dto)
        return resultado

    def asignar_tecnico(
        self, administrador: Administrador, id_incidencia: int, tecnico: Tecnico, prioridad: PrioridadEnum
    ) -> IncidenciaRespuestaDTO:
        if not administrador.tiene_permiso("asignar_responsable_incidencia"):
            raise AccesoDenegadoException("El usuario no tiene permiso para asignar tecnicos")
        incidencia = self._incidencias.obtener_por_id(id_incidencia)
        administrador.asignar_responsable_incidencia(incidencia, tecnico)
        incidencia.prioridad = prioridad
        if incidencia.estado == EstadoIncidenciaEnum.RECIBIDO:
            incidencia.cambiar_estado(EstadoIncidenciaEnum.PROGRAMADO)
        self._incidencias.actualizar(incidencia)
        if self._notificaciones is not None:
            self._notificaciones.notificar_asignacion(tecnico, incidencia)
            self._notificaciones.notificar_tecnico_asignado_a_docente(incidencia.docente, incidencia, tecnico)
        return IncidenciaRespuestaDTO.desde_incidencia(incidencia)

    def atender_incidencia(self, tecnico: Tecnico, id_incidencia: int) -> IncidenciaRespuestaDTO:
        incidencia = self._incidencias.obtener_por_id(id_incidencia)
        tecnico.atender_incidencia(incidencia)
        self._incidencias.actualizar(incidencia)
        if self._notificaciones is not None:
            self._notificaciones.notificar_cambio_estado(incidencia.docente, incidencia)
        return IncidenciaRespuestaDTO.desde_incidencia(incidencia)

    def cambiar_estado(self, tecnico: Tecnico, id_incidencia: int, nuevo_estado: EstadoIncidenciaEnum) -> IncidenciaRespuestaDTO:
        incidencia = self._incidencias.obtener_por_id(id_incidencia)
        if incidencia.tecnico_asignado is None or incidencia.tecnico_asignado.id_usuario != tecnico.id_usuario:
            raise AccesoDenegadoException("Solo el tecnico asignado puede actualizar este ticket")
        if nuevo_estado == EstadoIncidenciaEnum.RESUELTO and self._notas_tecnicas is not None:
            notas_publicas = [
                nota for nota in self._notas_tecnicas.listar_por_incidencia(id_incidencia) if not nota.es_privado
            ]
            if not notas_publicas:
                raise ValidacionException(
                    "Debe registrar una nota publica de diagnostico y solucion antes de resolver el ticket",
                    campo="estado",
                )
        tecnico.actualizar_estado_ticket(incidencia, nuevo_estado)
        self._incidencias.actualizar(incidencia)
        if self._notificaciones is not None:
            self._notificaciones.notificar_cambio_estado(incidencia.docente, incidencia)
        return IncidenciaRespuestaDTO.desde_incidencia(incidencia)

    def priorizar(self, id_incidencia: int, prioridad: PrioridadEnum) -> IncidenciaRespuestaDTO:
        incidencia = self._incidencias.obtener_por_id(id_incidencia)
        incidencia.prioridad = prioridad
        self._incidencias.actualizar(incidencia)
        return IncidenciaRespuestaDTO.desde_incidencia(incidencia)

    def listar_carga_tecnicos(self) -> dict[int, int]:
        """Cuenta tickets abiertos (no RESUELTO) por tecnico, para el modal de asignacion del admin."""
        conteo: dict[int, int] = {}
        for incidencia in self._incidencias.listar():
            if incidencia.tecnico_asignado is not None and incidencia.estado != EstadoIncidenciaEnum.RESUELTO:
                id_tecnico = incidencia.tecnico_asignado.id_usuario
                conteo[id_tecnico] = conteo.get(id_tecnico, 0) + 1
        return conteo

    def obtener_metricas_tecnico(self, tecnico: Tecnico) -> dict:
        ahora = datetime.now()
        tickets = self._incidencias.listar_por_tecnico(tecnico.id_usuario)
        pendientes = sum(1 for t in tickets if t.estado == EstadoIncidenciaEnum.PROGRAMADO)
        en_proceso = sum(1 for t in tickets if t.estado == EstadoIncidenciaEnum.EN_PROCESO)
        resueltos_mes = sum(
            1
            for t in tickets
            if t.estado == EstadoIncidenciaEnum.RESUELTO
            and t.fecha_resolucion is not None
            and t.fecha_resolucion.year == ahora.year
            and t.fecha_resolucion.month == ahora.month
        )
        return {"pendientes": pendientes, "en_proceso": en_proceso, "resueltos_mes": resueltos_mes}
