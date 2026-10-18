from app.dtos.respuesta_ia_dto import RespuestaIADTO
from app.dtos.sugerencia_ticket_dto import SugerenciaTicketDTO
from app.services.asistente_ia_service import AsistenteIAService
from app.utils.catalogo_incidencias import CatalogoIncidencias


class ChatbotService:
    """Asistente virtual de soporte Nivel 1: interpreta el mensaje y, si hace falta atencion
    presencial, propone los datos de un ticket para que el docente los revise y confirme
    desde el formulario (nunca lo crea por su cuenta) (RF3)."""

    def __init__(self, asistente_ia: AsistenteIAService):
        self._asistente_ia = asistente_ia

    def procesar_mensaje(self, mensaje: str, id_laboratorio: int, id_equipo: int | None = None) -> RespuestaIADTO:
        diagnostico = self._asistente_ia.analizar_texto(mensaje)
        sugerencias = self._asistente_ia.generar_sugerencia_autocorreccion(diagnostico.tipo_falla)

        if not self._asistente_ia.requiere_atencion_fisica(diagnostico):
            return RespuestaIADTO(
                respuesta="Antes de derivarlo a soporte tecnico, intenta estos pasos:",
                sugerencias=sugerencias,
                requiere_atencion_fisica=False,
            )

        sugerencia_ticket = SugerenciaTicketDTO(
            id_laboratorio=id_laboratorio,
            categoria=CatalogoIncidencias.categoria_por_tipo_falla(diagnostico.tipo_falla),
            tipo_falla=diagnostico.tipo_falla,
            descripcion=mensaje,
        )
        return RespuestaIADTO(
            respuesta="Esta falla requiere atencion tecnica presencial. Revisa los datos y confirma para crear el ticket.",
            sugerencias=sugerencias,
            requiere_atencion_fisica=True,
            sugerencia_ticket=sugerencia_ticket,
        )
