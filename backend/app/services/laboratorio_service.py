from app.dtos.laboratorio_dto import LaboratorioDTO
from app.exceptions import AccesoDenegadoException
from app.models.administrador import Administrador
from app.models.incidencia import Incidencia
from app.models.laboratorio import Laboratorio
from app.repositories.incidencia_repository import IncidenciaRepository
from app.repositories.laboratorio_repository import LaboratorioRepository


class LaboratorioService:
    """Alta, edicion y consulta de Laboratorio; solo accesible para un Administrador (UC11)."""

    def __init__(self, laboratorio_repository: LaboratorioRepository, incidencia_repository: IncidenciaRepository):
        self._laboratorios = laboratorio_repository
        self._incidencias = incidencia_repository

    def registrar_laboratorio(self, administrador: Administrador, datos: LaboratorioDTO) -> Laboratorio:
        self._exigir_permiso(administrador)
        laboratorio = Laboratorio(
            id_laboratorio=self._laboratorios.siguiente_id(),
            nombre=datos.nombre,
            pabellon=datos.pabellon,
            piso=datos.piso,
            estado_operativo=datos.estado_operativo,
        )
        self._laboratorios.agregar(laboratorio)
        return laboratorio

    def editar_laboratorio(self, administrador: Administrador, id_laboratorio: int, datos: LaboratorioDTO) -> Laboratorio:
        self._exigir_permiso(administrador)
        laboratorio = self._laboratorios.obtener_por_id(id_laboratorio)
        administrador.gestionar_laboratorio(
            laboratorio,
            nombre=datos.nombre,
            pabellon=datos.pabellon,
            piso=datos.piso,
            estado_operativo=datos.estado_operativo,
        )
        self._laboratorios.actualizar(laboratorio)
        return laboratorio

    def listar_laboratorios(self) -> list[Laboratorio]:
        return self._laboratorios.listar()

    def obtener_historial_incidencias(self, id_laboratorio: int) -> list[Incidencia]:
        laboratorio = self._laboratorios.obtener_por_id(id_laboratorio)
        return laboratorio.obtener_historial_incidencias(self._incidencias.listar())

    @staticmethod
    def _exigir_permiso(administrador: Administrador) -> None:
        if not administrador.tiene_permiso("gestionar_laboratorio"):
            raise AccesoDenegadoException("El usuario no tiene permiso para gestionar laboratorios")
