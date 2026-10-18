import secrets
import string

from app.dtos.usuario_dto import UsuarioDTO
from app.exceptions import AccesoDenegadoException, ValidacionException
from app.models.administrador import Administrador
from app.models.docente import Docente
from app.models.enums import RolEnum
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository

_ALFABETO_PASSWORD_TEMPORAL = string.ascii_letters + string.digits

_FABRICAS_POR_ROL = {
    RolEnum.ADMINISTRADOR: Administrador,
    RolEnum.DOCENTE: Docente,
}


class UsuarioService:
    """Alta, baja/reactivacion y listado de usuarios; solo accesible para un Administrador (UC10)."""

    def __init__(self, usuario_repository: UsuarioRepository):
        self._usuarios = usuario_repository

    def crear_y_registrar_usuario(
        self,
        administrador: Administrador,
        rol: RolEnum,
        codigo_ucv: str,
        nombre: str,
        apellido: str,
        email: str,
        password_plano: str,
        especialidad: str | None = None,
    ) -> UsuarioDTO:
        password_hash = Usuario.generar_password_hash(password_plano)
        id_usuario = self._usuarios.siguiente_id()
        if rol == RolEnum.TECNICO:
            if not especialidad:
                raise ValidacionException("El tecnico requiere especialidad", campo="especialidad")
            usuario = Tecnico(id_usuario, codigo_ucv, nombre, apellido, email, password_hash, especialidad=especialidad)
        else:
            clase = _FABRICAS_POR_ROL[rol]
            usuario = clase(id_usuario, codigo_ucv, nombre, apellido, email, password_hash)
        return self.registrar_usuario(administrador, usuario)

    def registrar_usuario(self, administrador: Administrador, usuario: Usuario) -> UsuarioDTO:
        self._exigir_permiso(administrador)
        if self._usuarios.buscar_por_codigo_ucv(usuario.codigo_ucv) is not None:
            raise ValidacionException("Ya existe un usuario con ese codigo UCV", campo="codigo_ucv")
        if self._usuarios.buscar_por_email(usuario.email) is not None:
            raise ValidacionException("Ya existe un usuario con ese email", campo="email")
        self._usuarios.agregar(usuario)
        return UsuarioDTO.desde_usuario(usuario)

    def cambiar_estado_usuario(self, administrador: Administrador, id_usuario: int, activo: bool) -> UsuarioDTO:
        self._exigir_permiso(administrador)
        usuario = self._usuarios.obtener_por_id(id_usuario)
        administrador.gestionar_usuario(usuario, activo)
        self._usuarios.actualizar(usuario)
        return UsuarioDTO.desde_usuario(usuario)

    def listar_usuarios(self, administrador: Administrador) -> list[UsuarioDTO]:
        self._exigir_permiso(administrador)
        return [UsuarioDTO.desde_usuario(usuario) for usuario in self._usuarios.listar()]

    def editar_usuario(
        self,
        administrador: Administrador,
        id_usuario: int,
        codigo_ucv: str,
        nombre: str,
        apellido: str,
        email: str,
        especialidad: str | None = None,
    ) -> UsuarioDTO:
        """Edita los datos de un usuario existente sin tocar su rol ni su contrasena."""
        self._exigir_permiso(administrador)
        usuario = self._usuarios.obtener_por_id(id_usuario)

        otro_con_codigo = self._usuarios.buscar_por_codigo_ucv(codigo_ucv)
        if otro_con_codigo is not None and otro_con_codigo.id_usuario != id_usuario:
            raise ValidacionException("Ya existe un usuario con ese codigo UCV", campo="codigo_ucv")
        otro_con_email = self._usuarios.buscar_por_email(email)
        if otro_con_email is not None and otro_con_email.id_usuario != id_usuario:
            raise ValidacionException("Ya existe un usuario con ese email", campo="email")

        usuario.codigo_ucv = codigo_ucv
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.email = email
        if isinstance(usuario, Tecnico) and especialidad:
            usuario.especialidad = especialidad
        self._usuarios.actualizar(usuario)
        return UsuarioDTO.desde_usuario(usuario)

    def restablecer_password(self, administrador: Administrador, id_usuario: int) -> str:
        """Genera una contrasena temporal, la guarda hasheada y la devuelve en texto plano una sola vez."""
        self._exigir_permiso(administrador)
        usuario = self._usuarios.obtener_por_id(id_usuario)
        password_temporal = "".join(secrets.choice(_ALFABETO_PASSWORD_TEMPORAL) for _ in range(10))
        usuario.restablecer_password(password_temporal)
        self._usuarios.actualizar(usuario)
        return password_temporal

    @staticmethod
    def _exigir_permiso(administrador: Administrador) -> None:
        if not administrador.tiene_permiso("gestionar_usuario"):
            raise AccesoDenegadoException("El usuario no tiene permiso para gestionar usuarios")
