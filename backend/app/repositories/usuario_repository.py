from app.config.database import DatabaseConnection
from app.exceptions import RecursoNoEncontradoException
from app.models.administrador import Administrador
from app.models.docente import Docente
from app.models.enums import RolEnum
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.repositories.base_repository import BaseRepository

_FABRICAS_SIMPLES = {
    RolEnum.ADMINISTRADOR: Administrador,
    RolEnum.DOCENTE: Docente,
}


class UsuarioRepository(BaseRepository[Usuario, int]):
    """Persistencia de Usuario y sus subclases (Administrador, Docente, Tecnico) en un solo
    almacen/tabla, usando la columna `rol` como discriminador para reconstruir la subclase
    correcta (especialidad/disponible solo aplican cuando rol = TECNICO)."""

    def __init__(self, database: DatabaseConnection | None = None):
        super().__init__(nombre_entidad="Usuario", database=database)

    def _obtener_id(self, entidad: Usuario) -> int:
        return entidad.id_usuario

    def siguiente_id(self) -> int:
        if not self._usa_sql:
            return super().siguiente_id()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ISNULL(MAX(id_usuario), 0) + 1 FROM usuarios")
            return cursor.fetchone()[0]
        finally:
            conexion.close()

    def agregar(self, entidad: Usuario) -> Usuario:
        if not self._usa_sql:
            return super().agregar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SET IDENTITY_INSERT usuarios ON")
            cursor.execute(
                "INSERT INTO usuarios (id_usuario, codigo_ucv, nombre, apellido, email, password_hash, "
                "rol, estado, especialidad, disponible) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                entidad.id_usuario,
                entidad.codigo_ucv,
                entidad.nombre,
                entidad.apellido,
                entidad.email,
                entidad._password_hash,
                entidad.obtener_rol().value,
                entidad.estado,
                getattr(entidad, "especialidad", None),
                getattr(entidad, "disponible", None),
            )
            cursor.execute("SET IDENTITY_INSERT usuarios OFF")
            conexion.commit()
        finally:
            conexion.close()
        return entidad

    def obtener_por_id(self, id_entidad: int) -> Usuario:
        if not self._usa_sql:
            return super().obtener_por_id(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"{_SELECT_USUARIOS} WHERE id_usuario = ?", id_entidad)
            fila = cursor.fetchone()
            if fila is None:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            return self._fila_a_usuario(fila)
        finally:
            conexion.close()

    def existe(self, id_entidad: int) -> bool:
        if not self._usa_sql:
            return super().existe(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 FROM usuarios WHERE id_usuario = ?", id_entidad)
            return cursor.fetchone() is not None
        finally:
            conexion.close()

    def listar(self) -> list[Usuario]:
        if not self._usa_sql:
            return super().listar()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(_SELECT_USUARIOS)
            return [self._fila_a_usuario(fila) for fila in cursor.fetchall()]
        finally:
            conexion.close()

    def actualizar(self, entidad: Usuario) -> Usuario:
        if not self._usa_sql:
            return super().actualizar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE usuarios SET codigo_ucv = ?, nombre = ?, apellido = ?, email = ?, password_hash = ?, "
                "estado = ?, especialidad = ?, disponible = ? WHERE id_usuario = ?",
                entidad.codigo_ucv,
                entidad.nombre,
                entidad.apellido,
                entidad.email,
                entidad._password_hash,
                entidad.estado,
                getattr(entidad, "especialidad", None),
                getattr(entidad, "disponible", None),
                entidad.id_usuario,
            )
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, entidad.id_usuario)
            conexion.commit()
        finally:
            conexion.close()
        return entidad

    def eliminar(self, id_entidad: int) -> None:
        if not self._usa_sql:
            return super().eliminar(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = ?", id_entidad)
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            conexion.commit()
        finally:
            conexion.close()

    def buscar_por_codigo_ucv(self, codigo_ucv: str) -> Usuario | None:
        if not self._usa_sql:
            return next((u for u in self.listar() if u.codigo_ucv == codigo_ucv), None)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"{_SELECT_USUARIOS} WHERE codigo_ucv = ?", codigo_ucv)
            fila = cursor.fetchone()
            return self._fila_a_usuario(fila) if fila else None
        finally:
            conexion.close()

    def buscar_por_email(self, email: str) -> Usuario | None:
        email_normalizado = email.strip().lower()
        if not self._usa_sql:
            return next((u for u in self.listar() if u.email == email_normalizado), None)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"{_SELECT_USUARIOS} WHERE email = ?", email_normalizado)
            fila = cursor.fetchone()
            return self._fila_a_usuario(fila) if fila else None
        finally:
            conexion.close()

    def listar_por_rol(self, rol: RolEnum) -> list[Usuario]:
        return [u for u in self.listar() if u.obtener_rol() == rol]

    def listar_tecnicos_disponibles(self) -> list[Usuario]:
        return [u for u in self.listar_por_rol(RolEnum.TECNICO) if getattr(u, "disponible", False)]

    @staticmethod
    def _fila_a_usuario(fila) -> Usuario:
        (
            id_usuario,
            codigo_ucv,
            nombre,
            apellido,
            email,
            password_hash,
            rol,
            estado,
            especialidad,
            disponible,
        ) = fila
        rol_enum = RolEnum(rol)
        if rol_enum == RolEnum.TECNICO:
            return Tecnico(
                id_usuario=id_usuario,
                codigo_ucv=codigo_ucv,
                nombre=nombre,
                apellido=apellido,
                email=email,
                password_hash=password_hash,
                especialidad=especialidad or "General",
                disponible=bool(disponible) if disponible is not None else True,
                estado=bool(estado),
            )
        clase = _FABRICAS_SIMPLES[rol_enum]
        return clase(
            id_usuario=id_usuario,
            codigo_ucv=codigo_ucv,
            nombre=nombre,
            apellido=apellido,
            email=email,
            password_hash=password_hash,
            estado=bool(estado),
        )


_SELECT_USUARIOS = (
    "SELECT id_usuario, codigo_ucv, nombre, apellido, email, password_hash, rol, estado, "
    "especialidad, disponible FROM usuarios"
)
