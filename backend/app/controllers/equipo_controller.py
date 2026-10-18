from typing import Callable

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dtos.equipo_dto import EquipoDTO
from app.models.administrador import Administrador
from app.models.enums import EstadoEquipoEnum
from app.models.usuario import Usuario
from app.services.equipo_service import EquipoService


class EquipoSchema(BaseModel):
    codigo_patrimonial: str
    tipo_equipo: str
    estado: EstadoEquipoEnum = EstadoEquipoEnum.OPERATIVO


class CambioEstadoEquipoSchema(BaseModel):
    estado: EstadoEquipoEnum


def crear_router_equipos(
    equipo_service: EquipoService,
    requiere_administrador: Callable[..., Administrador],
    requiere_tecnico_o_administrador: Callable[..., Usuario],
) -> APIRouter:
    """Endpoints de administracion de equipos (UC11)."""

    router = APIRouter(tags=["equipos"])

    @router.post("/laboratorios/{id_laboratorio}/equipos", status_code=201)
    def registrar_equipo(
        id_laboratorio: int, body: EquipoSchema, administrador: Administrador = Depends(requiere_administrador)
    ):
        datos = EquipoDTO(codigo_patrimonial=body.codigo_patrimonial, tipo_equipo=body.tipo_equipo, estado=body.estado)
        equipo = equipo_service.registrar_equipo(administrador, id_laboratorio, datos)
        return _a_respuesta(equipo)

    @router.get("/laboratorios/{id_laboratorio}/equipos")
    def listar_equipos(id_laboratorio: int):
        return [_a_respuesta(e) for e in equipo_service.listar_por_laboratorio(id_laboratorio)]

    @router.patch("/equipos/{id_equipo}/estado")
    def cambiar_estado_equipo(
        id_equipo: int, body: CambioEstadoEquipoSchema, _: Usuario = Depends(requiere_tecnico_o_administrador)
    ):
        equipo = equipo_service.cambiar_estado(id_equipo, body.estado)
        return _a_respuesta(equipo)

    return router


def _a_respuesta(equipo) -> dict:
    return {
        "id_equipo": equipo.id_equipo,
        "codigo_patrimonial": equipo.codigo_patrimonial,
        "tipo_equipo": equipo.tipo_equipo,
        "estado": equipo.estado,
    }
