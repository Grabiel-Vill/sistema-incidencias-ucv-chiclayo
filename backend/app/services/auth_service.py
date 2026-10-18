from datetime import datetime, timedelta

from app.config.security_config import SecurityConfig
from app.dtos.credenciales_dto import CredencialesDTO
from app.dtos.token_dto import TokenDTO
from app.exceptions import CredencialesInvalidasException
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository


class AuthService:
    """Valida credenciales UCV, emite/valida tokens de sesion y cierra sesion."""

    def __init__(self, usuario_repository: UsuarioRepository, security_config: SecurityConfig):
        self._usuarios = usuario_repository
        self._security = security_config

    def iniciar_sesion(self, credenciales: CredencialesDTO) -> TokenDTO:
        usuario = self._usuarios.buscar_por_email(credenciales.email)
        if usuario is None:
            raise CredencialesInvalidasException()

        sesion = usuario.iniciar_sesion(credenciales.password)
        access_token = self._security.generar_token(sesion)
        expiracion = datetime.now() + timedelta(minutes=self._security.jwt_expiracion_minutos)
        return TokenDTO(access_token=access_token, rol=sesion["rol"], expiracion=expiracion.isoformat())

    def cerrar_sesion(self, usuario: Usuario) -> None:
        usuario.cerrar_sesion()

    def validar_token(self, token: str) -> dict:
        return self._security.validar_token(token)

    def obtener_usuario_autenticado(self, token: str) -> Usuario:
        payload = self.validar_token(token)
        return self._usuarios.obtener_por_id(payload["id_usuario"])
