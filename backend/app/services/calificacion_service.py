from app.dtos.calificacion_dto import CalificacionRespuestaDTO
from app.exceptions import AccesoDenegadoException, ValidacionException
from app.models.calificacion import Calificacion
from app.models.docente import Docente
from app.models.enums import EstadoIncidenciaEnum
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.incidencia_repository import IncidenciaRepository


class CalificacionService:
    """Permite al Docente dueño de un ticket RESUELTO calificar al Tecnico una sola vez (sec. 3d)."""

    def __init__(self, calificacion_repository: CalificacionRepository, incidencia_repository: IncidenciaRepository):
        self._calificaciones = calificacion_repository
        self._incidencias = incidencia_repository

    def calificar(
        self, docente: Docente, id_incidencia: int, estrellas: int, comentario: str | None
    ) -> CalificacionRespuestaDTO:
        incidencia = self._incidencias.obtener_por_id(id_incidencia)
        if incidencia.docente.id_usuario != docente.id_usuario:
            raise AccesoDenegadoException("Solo el docente que reporto el ticket puede calificarlo")
        if incidencia.estado != EstadoIncidenciaEnum.RESUELTO:
            raise ValidacionException("Solo se puede calificar un ticket RESUELTO", campo="estado")
        if incidencia.tecnico_asignado is None:
            raise ValidacionException("El ticket no tiene un tecnico asignado para calificar", campo="id_tecnico")
        if self._calificaciones.buscar_por_incidencia(id_incidencia) is not None:
            raise ValidacionException("Este ticket ya fue calificado", campo="id_incidencia")

        calificacion = Calificacion(
            id_calificacion=self._calificaciones.siguiente_id(),
            id_incidencia=id_incidencia,
            id_docente=docente.id_usuario,
            id_tecnico=incidencia.tecnico_asignado.id_usuario,
            estrellas=estrellas,
            comentario=comentario,
        )
        self._calificaciones.agregar(calificacion)
        return CalificacionRespuestaDTO.desde_calificacion(calificacion)
