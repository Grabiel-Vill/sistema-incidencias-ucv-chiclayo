from datetime import datetime
from typing import Callable

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

from app.dtos.calificacion_dto import CalificacionRespuestaDTO
from app.dtos.filtro_dto import FiltroDTO
from app.dtos.incidencia_dto import IncidenciaDTO
from app.dtos.incidencia_respuesta_dto import IncidenciaRespuestaDTO
from app.models.administrador import Administrador
from app.models.docente import Docente
from app.models.enums import EstadoIncidenciaEnum, PrioridadEnum, RolEnum, TipoFallaEnum, TipoRequerimientoEnum
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.services.calificacion_service import CalificacionService
from app.services.incidencia_service import IncidenciaService
from app.utils.catalogo_incidencias import CatalogoIncidencias


class IncidenciaSchema(BaseModel):
    descripcion: str
    id_laboratorio: int
    tipo_falla: TipoFallaEnum | None = None
    id_equipo: int | None = None
    tipo_requerimiento: TipoRequerimientoEnum = TipoRequerimientoEnum.FALLA_TECNICA
    fecha_hora_apertura: datetime | None = None
    subcategoria: str | None = None

    @field_validator("fecha_hora_apertura")
    @classmethod
    def _normalizar_fecha_apertura(cls, valor: datetime | None) -> datetime | None:
        if valor is not None and valor.tzinfo is not None:
            return valor.astimezone().replace(tzinfo=None)
        return valor


class AsignarTecnicoSchema(BaseModel):
    id_tecnico: int
    prioridad: PrioridadEnum = PrioridadEnum.MEDIA


class CambioEstadoSchema(BaseModel):
    estado: EstadoIncidenciaEnum


class PriorizarSchema(BaseModel):
    prioridad: PrioridadEnum


class CalificacionSchema(BaseModel):
    estrellas: int
    comentario: str | None = None


def crear_router_incidencias(
    incidencia_service: IncidenciaService,
    calificacion_service: CalificacionService,
    usuario_repository: UsuarioRepository,
    obtener_usuario_actual: Callable[..., Usuario],
    requiere_docente: Callable[..., Docente],
    requiere_tecnico: Callable[..., Tecnico],
    requiere_administrador: Callable[..., Administrador],
    requiere_tecnico_o_administrador: Callable[..., Usuario],
) -> APIRouter:
    """Endpoints de registro, consulta, asignacion y atencion de incidencias (RF1, RF2, RF4)."""

    router = APIRouter(prefix="/incidencias", tags=["incidencias"])

    @router.post("", response_model=IncidenciaRespuestaDTO, status_code=201)
    def registrar_incidencia(
        body: IncidenciaSchema, docente: Docente = Depends(requiere_docente)
    ) -> IncidenciaRespuestaDTO:
        datos = IncidenciaDTO(
            descripcion=body.descripcion,
            tipo_falla=body.tipo_falla,
            id_laboratorio=body.id_laboratorio,
            id_equipo=body.id_equipo,
            tipo_requerimiento=body.tipo_requerimiento,
            fecha_hora_apertura=body.fecha_hora_apertura,
            subcategoria=body.subcategoria,
        )
        return incidencia_service.registrar_incidencia(docente, datos)

    @router.get("/mias", response_model=list[IncidenciaRespuestaDTO])
    def listar_mis_incidencias(docente: Docente = Depends(requiere_docente)) -> list[IncidenciaRespuestaDTO]:
        return incidencia_service.listar_mias(docente)

    @router.get("/catalogo")
    def obtener_catalogo(_: Usuario = Depends(obtener_usuario_actual)) -> list[dict]:
        return CatalogoIncidencias.obtener()

    @router.get("/mis-metricas")
    def obtener_mis_metricas(tecnico: Tecnico = Depends(requiere_tecnico)) -> dict:
        return incidencia_service.obtener_metricas_tecnico(tecnico)

    @router.get("/tecnicos/carga")
    def obtener_carga_tecnicos(_: Administrador = Depends(requiere_administrador)) -> dict[int, int]:
        return incidencia_service.listar_carga_tecnicos()

    @router.get("/{id_incidencia}", response_model=IncidenciaRespuestaDTO)
    def obtener_incidencia(
        id_incidencia: int, _: Usuario = Depends(obtener_usuario_actual)
    ) -> IncidenciaRespuestaDTO:
        return incidencia_service.obtener_por_id(id_incidencia)

    @router.get("", response_model=list[IncidenciaRespuestaDTO])
    def listar_incidencias(
        id_laboratorio: int | None = None,
        tipo_falla: TipoFallaEnum | None = None,
        estado: EstadoIncidenciaEnum | None = None,
        id_tecnico: int | None = None,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        usuario: Usuario = Depends(requiere_tecnico_o_administrador),
    ) -> list[IncidenciaRespuestaDTO]:
        # Un tecnico solo puede ver SUS tickets: se ignora cualquier id_tecnico que mande el
        # cliente y se fuerza el propio (la restriccion vive en el backend, no solo en la UI).
        if usuario.obtener_rol() == RolEnum.TECNICO:
            id_tecnico = usuario.id_usuario
        filtro = FiltroDTO(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            id_laboratorio=id_laboratorio,
            tipo_falla=tipo_falla,
            estado=estado,
            id_tecnico=id_tecnico,
        )
        return incidencia_service.listar_con_filtro(filtro)

    @router.post("/{id_incidencia}/asignar", response_model=IncidenciaRespuestaDTO)
    def asignar_tecnico(
        id_incidencia: int, body: AsignarTecnicoSchema, administrador: Administrador = Depends(requiere_administrador)
    ) -> IncidenciaRespuestaDTO:
        tecnico = usuario_repository.obtener_por_id(body.id_tecnico)
        return incidencia_service.asignar_tecnico(administrador, id_incidencia, tecnico, body.prioridad)

    @router.post("/{id_incidencia}/atender", response_model=IncidenciaRespuestaDTO)
    def atender_incidencia(
        id_incidencia: int, tecnico: Tecnico = Depends(requiere_tecnico)
    ) -> IncidenciaRespuestaDTO:
        return incidencia_service.atender_incidencia(tecnico, id_incidencia)

    @router.patch("/{id_incidencia}/estado", response_model=IncidenciaRespuestaDTO)
    def cambiar_estado(
        id_incidencia: int, body: CambioEstadoSchema, tecnico: Tecnico = Depends(requiere_tecnico)
    ) -> IncidenciaRespuestaDTO:
        return incidencia_service.cambiar_estado(tecnico, id_incidencia, body.estado)

    @router.patch("/{id_incidencia}/prioridad", response_model=IncidenciaRespuestaDTO)
    def priorizar(
        id_incidencia: int, body: PriorizarSchema, _: Usuario = Depends(requiere_tecnico_o_administrador)
    ) -> IncidenciaRespuestaDTO:
        return incidencia_service.priorizar(id_incidencia, body.prioridad)

    @router.post("/{id_incidencia}/calificacion", response_model=CalificacionRespuestaDTO, status_code=201)
    def calificar_incidencia(
        id_incidencia: int, body: CalificacionSchema, docente: Docente = Depends(requiere_docente)
    ) -> CalificacionRespuestaDTO:
        return calificacion_service.calificar(docente, id_incidencia, body.estrellas, body.comentario)

    return router
