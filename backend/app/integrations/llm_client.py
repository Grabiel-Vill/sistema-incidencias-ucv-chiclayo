import json
import urllib.error
import urllib.request

from app.config.llm_config import LLMConfig
from app.dtos.diagnostico_dto import DiagnosticoDTO
from app.models.enums import PrioridadEnum, TipoFallaEnum

_ENDPOINT = "https://api.anthropic.com/v1/messages"


class LLMClient:
    """Cliente HTTP hacia la API del modelo de lenguaje usado por AsistenteIAService (RF3).

    Requiere LLM_API_KEY configurada y acceso a internet; AsistenteIAService lo usa como
    primera opcion y se degrada a su heuristica local si esta clase falla (RNF3).
    """

    def __init__(self, llm_config: LLMConfig):
        self._config = llm_config

    def generar_diagnostico(self, descripcion: str) -> DiagnosticoDTO:
        if not self._config.esta_configurado:
            raise RuntimeError("LLM_API_KEY no esta configurada")

        cuerpo = json.dumps(
            {
                "model": self._config.modelo,
                "max_tokens": self._config.max_tokens,
                "temperature": self._config.temperatura,
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Clasifica esta falla de laboratorio y responde unicamente con JSON de la forma "
                            '{"tipo_falla": "HARDWARE|RED|ELECTRICIDAD|ILUMINACION", "diagnostico": "string", '
                            f'"prioridad": "ALTA|MEDIA|BAJA"}}. Descripcion: {descripcion}'
                        ),
                    }
                ],
            }
        ).encode("utf-8")

        peticion = urllib.request.Request(
            _ENDPOINT,
            data=cuerpo,
            method="POST",
            headers={
                "content-type": "application/json",
                "x-api-key": self._config.api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        try:
            with urllib.request.urlopen(peticion, timeout=15) as respuesta:
                datos = json.loads(respuesta.read())
        except urllib.error.URLError as exc:
            raise RuntimeError(f"No se pudo contactar al proveedor de IA: {exc}") from exc

        resultado = json.loads(datos["content"][0]["text"])
        return DiagnosticoDTO(
            tipo_falla=TipoFallaEnum(resultado["tipo_falla"]),
            diagnostico=resultado["diagnostico"],
            prioridad=PrioridadEnum(resultado["prioridad"]),
        )
