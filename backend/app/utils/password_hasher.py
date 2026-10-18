import hashlib
import hmac
import os

_ALGORITMO = "pbkdf2_sha256"
_ITERACIONES = 390_000


class PasswordHasher:
    """Hash y verificacion de contrasenas con PBKDF2-HMAC-SHA256 y salt aleatorio por usuario."""

    @staticmethod
    def hash_password(password_plano: str) -> str:
        salt = os.urandom(16)
        derivado = hashlib.pbkdf2_hmac("sha256", password_plano.encode("utf-8"), salt, _ITERACIONES)
        return f"{_ALGORITMO}${_ITERACIONES}${salt.hex()}${derivado.hex()}"

    @staticmethod
    def verificar_password(password_plano: str, password_hash: str) -> bool:
        try:
            algoritmo, iteraciones, salt_hex, hash_hex = password_hash.split("$")
        except ValueError:
            return False
        if algoritmo != _ALGORITMO:
            return False
        salt = bytes.fromhex(salt_hex)
        derivado = hashlib.pbkdf2_hmac("sha256", password_plano.encode("utf-8"), salt, int(iteraciones))
        return hmac.compare_digest(derivado.hex(), hash_hex)
