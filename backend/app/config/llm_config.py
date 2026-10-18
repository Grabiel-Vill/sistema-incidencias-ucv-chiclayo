from app.config.settings import Settings


class LLMConfig:
    """API key, modelo y parametros del proveedor de IA usado por AsistenteIA/ChatbotService (RF3)."""

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()
        self.api_key = self._settings.obtener("LLM_API_KEY")
        self.modelo = self._settings.obtener("LLM_MODEL", "claude-sonnet-5")
        self.max_tokens = self._settings.obtener_entero("LLM_MAX_TOKENS", 1024)
        self.temperatura = float(self._settings.obtener("LLM_TEMPERATURE", "0.3"))

    @property
    def esta_configurado(self) -> bool:
        return bool(self.api_key)
