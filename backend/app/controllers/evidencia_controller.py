from typing import Callable

from fastapi import APIRouter, Depends, File, UploadFile

from app.models.usuario import Usuario
from app.repositories.incidencia_repository import IncidenciaRepository
from app.services.evidencia_service import EvidenciaService


def crear_router_evidencias(
    evidencia_service: EvidenciaService,
    incidencia_repository: IncidenciaRepository,
    obtener_usuario_actual: Callable[..., Usuario],
) -> APIRouter:
    """Endpoints para adjuntar evidencia fotografica a una Incidencia (RF1)."""

    router = APIRouter(prefix="/incidencias/{id_incidencia}/evidencias", tags=["evidencias"])

    @router.post("", status_code=201)
    async def agregar_evidencia(
        id_incidencia: int, archivo: UploadFile = File(...), _: Usuario = Depends(obtener_usuario_actual)
    ):
        incidencia = incidencia_repository.obtener_por_id(id_incidencia)
        contenido = await archivo.read()
        evidencia = evidencia_service.agregar_evidencia(incidencia, archivo.filename, contenido)
        return {"id_evidencia": evidencia.id_evidencia, "url_imagen": evidencia.url_imagen}

    @router.get("")
    def listar_evidencias(id_incidencia: int, _: Usuario = Depends(obtener_usuario_actual)):
        incidencia = incidencia_repository.obtener_por_id(id_incidencia)
        return [{"id_evidencia": e.id_evidencia, "url_imagen": e.url_imagen} for e in incidencia.evidencias]

    return router
