from app.dtos.nota_tecnica_dto import NotaTecnicaDTO
from app.exceptions import AccesoDenegadoException
from app.models.nota_tecnica import NotaTecnica
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.repositories.incidencia_repository import IncidenciaRepository
from app.repositories.nota_tecnica_repository import NotaTecnicaRepository


class NotaTecnicaService:
    """Agrega notas internas/publicas a una Incidencia y filtra su visibilidad por rol (RF4)."""

    def __init__(self, nota_tecnica_repository: NotaTecnicaRepository, incidencia_repository: IncidenciaRepository):
        self._notas = nota_tecnica_repository
        self._incidencias = incidencia_repository

    def agregar_nota(self, tecnico: Tecnico, id_incidencia: int, datos: NotaTecnicaDTO) -> NotaTecnica:
        incidencia = self._incidencias.obtener_por_id(id_incidencia)
        if incidencia.tecnico_asignado is None or incidencia.tecnico_asignado.id_usuario != tecnico.id_usuario:
            raise AccesoDenegadoException("Solo el tecnico asignado puede agregar notas a este ticket")
        nota = tecnico.agregar_nota_tecnica(
            incidencia, id_nota=self._notas.siguiente_id(), contenido=datos.contenido, es_privado=datos.es_privado
        )
        self._notas.agregar(nota)
        self._incidencias.actualizar(incidencia)
        return nota

    def listar_visibles_para(self, usuario: Usuario, id_incidencia: int) -> list[NotaTecnica]:
        incidencia = self._incidencias.obtener_por_id(id_incidencia)
        return [nota for nota in incidencia.notas_tecnicas if nota.es_visible_para(usuario)]
