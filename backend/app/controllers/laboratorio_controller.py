from typing import Callable

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dtos.laboratorio_dto import LaboratorioDTO
from app.models.administrador import Administrador
from app.services.laboratorio_service import LaboratorioService


class LaboratorioSchema(BaseModel):
    nombre: str
    pabellon: str
    piso: int
    estado_operativo: bool = True


def crear_router_laboratorios(
    laboratorio_service: LaboratorioService, requiere_administrador: Callable[..., Administrador]
) -> APIRouter:
    """Endpoints de administracion de laboratorios (UC11)."""

    router = APIRouter(prefix="/laboratorios", tags=["laboratorios"])

    @router.post("", status_code=201)
    def registrar_laboratorio(body: LaboratorioSchema, administrador: Administrador = Depends(requiere_administrador)):
        laboratorio = laboratorio_service.registrar_laboratorio(administrador, _a_dto(body))
        return _a_respuesta(laboratorio)

    @router.put("/{id_laboratorio}")
    def editar_laboratorio(
        id_laboratorio: int, body: LaboratorioSchema, administrador: Administrador = Depends(requiere_administrador)
    ):
        laboratorio = laboratorio_service.editar_laboratorio(administrador, id_laboratorio, _a_dto(body))
        return _a_respuesta(laboratorio)

    @router.get("")
    def listar_laboratorios():
        return [_a_respuesta(lab) for lab in laboratorio_service.listar_laboratorios()]

    @router.get("/{id_laboratorio}/historial")
    def obtener_historial(id_laboratorio: int):
        return [i.codigo_ticket for i in laboratorio_service.obtener_historial_incidencias(id_laboratorio)]

    return router


def _a_dto(body: LaboratorioSchema) -> LaboratorioDTO:
    return LaboratorioDTO(nombre=body.nombre, pabellon=body.pabellon, piso=body.piso, estado_operativo=body.estado_operativo)


def _a_respuesta(laboratorio) -> dict:
    return {
        "id_laboratorio": laboratorio.id_laboratorio,
        "nombre": laboratorio.nombre,
        "pabellon": laboratorio.pabellon,
        "piso": laboratorio.piso,
        "estado_operativo": laboratorio.estado_operativo,
    }
