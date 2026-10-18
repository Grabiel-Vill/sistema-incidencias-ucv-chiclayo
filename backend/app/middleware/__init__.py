from app.middleware.auth_middleware import crear_dependencia_usuario_actual
from app.middleware.error_handler import registrar_manejadores_de_error
from app.middleware.role_middleware import crear_dependencia_rol

__all__ = [
    "crear_dependencia_rol",
    "crear_dependencia_usuario_actual",
    "registrar_manejadores_de_error",
]
