from typing import Callable

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dtos.respuesta_ia_dto import RespuestaIADTO
from app.models.docente import Docente
from app.services.chatbot_service import ChatbotService


class MensajeChatbotSchema(BaseModel):
    mensaje: str
    id_laboratorio: int
    id_equipo: int | None = None


def crear_router_chatbot(chatbot_service: ChatbotService, requiere_docente: Callable[..., Docente]) -> APIRouter:
    """Endpoints del asistente virtual de soporte Nivel 1 (RF3, UC03/UC04)."""

    router = APIRouter(prefix="/chatbot", tags=["chatbot"])

    @router.post("/mensaje", response_model=RespuestaIADTO)
    def procesar_mensaje(body: MensajeChatbotSchema, _: Docente = Depends(requiere_docente)) -> RespuestaIADTO:
        return chatbot_service.procesar_mensaje(body.mensaje, body.id_laboratorio, body.id_equipo)

    return router
