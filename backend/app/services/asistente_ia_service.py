from __future__ import annotations

from typing import TYPE_CHECKING

from app.dtos.diagnostico_dto import DiagnosticoDTO
from app.models.enums import PrioridadEnum, TipoFallaEnum

if TYPE_CHECKING:
    from app.integrations.llm_client import LLMClient

_PALABRAS_CLAVE_TIPO_FALLA: dict[TipoFallaEnum, tuple[str, ...]] = {
    TipoFallaEnum.RED: ("red", "internet", "wifi", "conexion", "ethernet"),
    TipoFallaEnum.ELECTRICIDAD: ("electric", "enchufe", "corriente", "tomacorriente", "apagon"),
    TipoFallaEnum.ILUMINACION: ("luz", "foco", "lampara", "iluminacion", "fluorescente"),
    TipoFallaEnum.HARDWARE: ("pc", "computadora", "monitor", "proyector", "teclado", "mouse", "pantalla"),
}

_PALABRAS_CLAVE_PRIORIDAD_ALTA = ("examen", "urgente", "ahora mismo", "no enciende nada", "toda el aula", "humo")

_SUGERENCIAS_AUTOCORRECCION: dict[TipoFallaEnum, tuple[str, ...]] = {
    TipoFallaEnum.RED: (
        "Verifica que el cable de red este bien conectado",
        "Reinicia el router/switch del laboratorio",
        "Olvida y reconecta la red WiFi institucional",
    ),
    TipoFallaEnum.HARDWARE: (
        "Reinicia el equipo manteniendo presionado el boton de encendido 10 segundos",
        "Verifica que los cables de monitor, teclado y mouse esten bien conectados",
    ),
    TipoFallaEnum.ELECTRICIDAD: (
        "Revisa que el tomacorriente o regleta tenga el interruptor encendido",
        "Prueba el equipo en otro tomacorriente antes de reportarlo como falla electrica",
    ),
    TipoFallaEnum.ILUMINACION: (
        "Verifica el interruptor de luces del ambiente",
        "Espera unos segundos, algunos fluorescentes demoran en encender",
    ),
}


class AsistenteIAService:
    """Clasifica y prioriza descripciones en lenguaje natural (RF3).

    Usa el LLMClient si esta disponible; ante cualquier falla (sin API key, sin red, respuesta
    invalida) se degrada a una heuristica local por palabras clave, sin interrumpir al usuario
    que esta reportando una falla (tolerancia a fallas, RNF3).
    """

    def __init__(self, llm_client: "LLMClient | None" = None):
        self._llm_client = llm_client

    def analizar_texto(self, descripcion: str) -> DiagnosticoDTO:
        if self._llm_client is not None:
            try:
                return self._llm_client.generar_diagnostico(descripcion)
            except Exception:
                pass
        return self._clasificar_con_heuristica(descripcion)

    def clasificar_y_priorizar(self, descripcion: str) -> DiagnosticoDTO:
        return self.analizar_texto(descripcion)

    def generar_sugerencia_autocorreccion(self, tipo_falla: TipoFallaEnum) -> list[str]:
        return list(_SUGERENCIAS_AUTOCORRECCION.get(tipo_falla, ()))

    def requiere_atencion_fisica(self, diagnostico: DiagnosticoDTO) -> bool:
        if diagnostico.prioridad == PrioridadEnum.ALTA:
            return True
        return diagnostico.tipo_falla in (TipoFallaEnum.ELECTRICIDAD, TipoFallaEnum.HARDWARE)

    @staticmethod
    def _clasificar_con_heuristica(descripcion: str) -> DiagnosticoDTO:
        texto = descripcion.lower()
        tipo_falla = TipoFallaEnum.HARDWARE
        for tipo, palabras in _PALABRAS_CLAVE_TIPO_FALLA.items():
            if any(palabra in texto for palabra in palabras):
                tipo_falla = tipo
                break

        prioridad = (
            PrioridadEnum.ALTA
            if any(palabra in texto for palabra in _PALABRAS_CLAVE_PRIORIDAD_ALTA)
            else PrioridadEnum.MEDIA
        )
        return DiagnosticoDTO(
            tipo_falla=tipo_falla,
            diagnostico=f"Clasificado automaticamente como {tipo_falla.value} a partir de la descripcion",
            prioridad=prioridad,
        )
