from typing import Callable

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dtos.nota_tecnica_dto import NotaTecnicaDTO
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.services.nota_tecnica_service import NotaTecnicaService


class NotaTecnicaSchema(BaseModel):
    contenido: str
    es_privado: bool = True


def crear_router_notas_tecnicas(
    nota_tecnica_service: NotaTecnicaService,
    obtener_usuario_actual: Callable[..., Usuario],
    requiere_tecnico: Callable[..., Tecnico],
) -> APIRouter:
    """Endpoints de notas internas/publicas sobre una Incidencia (RF4)."""

    router = APIRouter(prefix="/incidencias/{id_incidencia}/notas", tags=["notas-tecnicas"])

    @router.post("", status_code=201)
    def agregar_nota(
        id_incidencia: int, body: NotaTecnicaSchema, tecnico: Tecnico = Depends(requiere_tecnico)
    ):
        nota = nota_tecnica_service.agregar_nota(
            tecnico, id_incidencia, NotaTecnicaDTO(contenido=body.contenido, es_privado=body.es_privado)
        )
        return {"id_nota": nota.id_nota, "contenido": nota.contenido, "es_privado": nota.es_privado}

    @router.get("")
    def listar_notas(id_incidencia: int, usuario: Usuario = Depends(obtener_usuario_actual)):
        notas = nota_tecnica_service.listar_visibles_para(usuario, id_incidencia)
        return [{"id_nota": n.id_nota, "contenido": n.contenido, "es_privado": n.es_privado} for n in notas]

    return router
