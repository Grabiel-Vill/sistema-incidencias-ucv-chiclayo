from app.dtos.equipo_dto import EquipoDTO
from app.exceptions import AccesoDenegadoException
from app.models.administrador import Administrador
from app.models.enums import EstadoEquipoEnum
from app.models.equipo import Equipo
from app.repositories.equipo_repository import EquipoRepository
from app.repositories.laboratorio_repository import LaboratorioRepository


class EquipoService:
    """Alta y cambio de estado de Equipo dentro de un Laboratorio (UC11)."""

    def __init__(self, equipo_repository: EquipoRepository, laboratorio_repository: LaboratorioRepository):
        self._equipos = equipo_repository
        self._laboratorios = laboratorio_repository

    def registrar_equipo(self, administrador: Administrador, id_laboratorio: int, datos: EquipoDTO) -> Equipo:
        if not administrador.tiene_permiso("gestionar_laboratorio"):
            raise AccesoDenegadoException("El usuario no tiene permiso para gestionar equipos")
        laboratorio = self._laboratorios.obtener_por_id(id_laboratorio)
        equipo = Equipo(
            id_equipo=self._equipos.siguiente_id(),
            codigo_patrimonial=datos.codigo_patrimonial,
            tipo_equipo=datos.tipo_equipo,
            estado=datos.estado,
        )
        laboratorio.agregar_equipo(equipo)
        self._equipos.agregar(equipo)
        return equipo

    def cambiar_estado(self, id_equipo: int, nuevo_estado: EstadoEquipoEnum) -> Equipo:
        equipo = self._equipos.obtener_por_id(id_equipo)
        equipo.cambiar_estado(nuevo_estado)
        self._equipos.actualizar(equipo)
        return equipo

    def listar_por_laboratorio(self, id_laboratorio: int) -> list[Equipo]:
        return self._laboratorios.obtener_por_id(id_laboratorio).equipos
