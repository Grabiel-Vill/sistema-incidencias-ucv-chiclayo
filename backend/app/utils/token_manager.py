import base64
import hashlib
import hmac
import json
import time

from app.exceptions import CredencialesInvalidasException


class TokenManager:
    """Genera y valida tokens firmados (HMAC-SHA256), estilo JWT, sin depender de una libreria externa."""

    @staticmethod
    def generar_token(payload: dict, secreto: str, expiracion_minutos: int = 60) -> str:
        cuerpo = dict(payload)
        cuerpo["exp"] = int(time.time()) + expiracion_minutos * 60
        cuerpo_codificado = TokenManager._codificar(json.dumps(cuerpo, default=str).encode("utf-8"))
        firma = TokenManager._firmar(cuerpo_codificado, secreto)
        return f"{cuerpo_codificado}.{firma}"

    @staticmethod
    def decodificar_token(token: str, secreto: str) -> dict:
        try:
            cuerpo_codificado, firma = token.split(".")
        except ValueError:
            raise CredencialesInvalidasException("Token con formato invalido")

        firma_esperada = TokenManager._firmar(cuerpo_codificado, secreto)
        if not hmac.compare_digest(firma, firma_esperada):
            raise CredencialesInvalidasException("Token con firma invalida")

        payload = json.loads(TokenManager._decodificar(cuerpo_codificado))
        if payload.get("exp", 0) < time.time():
            raise CredencialesInvalidasException("Token expirado")
        return payload

    @staticmethod
    def _firmar(cuerpo_codificado: str, secreto: str) -> str:
        return hmac.new(secreto.encode("utf-8"), cuerpo_codificado.encode("utf-8"), hashlib.sha256).hexdigest()

    @staticmethod
    def _codificar(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

    @staticmethod
    def _decodificar(data: str) -> bytes:
        relleno = "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode(data + relleno)
