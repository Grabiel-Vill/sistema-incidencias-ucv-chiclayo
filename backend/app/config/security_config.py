import secrets

from app.config.settings import Settings
from app.utils.token_manager import TokenManager


class SecurityConfig:
    """Parametros de seguridad: secreto/expiracion JWT, HTTPS obligatorio y CORS (RNF4)."""

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()
        self._jwt_secreto_configurado = self._settings.obtener("JWT_SECRET") is not None
        self._jwt_secreto = self._settings.obtener("JWT_SECRET") or secrets.token_hex(32)
        self.jwt_expiracion_minutos = self._settings.obtener_entero("JWT_EXPIRACION_MINUTOS", 60)
        self.https_obligatorio = self._settings.obtener_booleano("HTTPS_OBLIGATORIO", True)
        self.cors_origenes_permitidos = self._settings.obtener_lista("CORS_ORIGENES_PERMITIDOS")

    @property
    def jwt_secreto_configurado(self) -> bool:
        return self._jwt_secreto_configurado

    def generar_token(self, payload: dict) -> str:
        return TokenManager.generar_token(payload, secreto=self._jwt_secreto, expiracion_minutos=self.jwt_expiracion_minutos)

    def validar_token(self, token: str) -> dict:
        return TokenManager.decodificar_token(token, secreto=self._jwt_secreto)
