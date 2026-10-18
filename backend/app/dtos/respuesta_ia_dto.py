from dataclasses import dataclass, field

from app.dtos.sugerencia_ticket_dto import SugerenciaTicketDTO


@dataclass(frozen=True)
class RespuestaIADTO:
    """Respuesta del chatbot de soporte Nivel 1: mensaje, pasos de autocorreccion o una sugerencia
    de ticket para que el docente la revise y confirme desde el formulario (RF3)."""

    respuesta: str
    sugerencias: list[str] = field(default_factory=list)
    requiere_atencion_fisica: bool = False
    sugerencia_ticket: SugerenciaTicketDTO | None = None
