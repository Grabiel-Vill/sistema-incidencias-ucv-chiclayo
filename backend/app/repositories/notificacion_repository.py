from app.config.database import DatabaseConnection
from app.exceptions import RecursoNoEncontradoException
from app.models.enums import PrioridadEnum, TipoNotificacionEnum
from app.models.notificacion import Notificacion
from app.repositories.base_repository import BaseRepository


class NotificacionRepository(BaseRepository[Notificacion, int]):
    """Persistencia de Notificacion. `entidad.id_usuario` ya viene poblado por
    Notificacion.enviar_notificacion() antes de que el servicio llame a agregar()."""

    def __init__(self, database: DatabaseConnection | None = None):
        super().__init__(nombre_entidad="Notificacion", database=database)

    def _obtener_id(self, entidad: Notificacion) -> int:
        return entidad.id_notificacion

    def siguiente_id(self) -> int:
        if not self._usa_sql:
            return super().siguiente_id()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ISNULL(MAX(id_notificacion), 0) + 1 FROM notificaciones")
            return cursor.fetchone()[0]
        finally:
            conexion.close()

    def agregar(self, entidad: Notificacion) -> Notificacion:
        if not self._usa_sql:
            return super().agregar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SET IDENTITY_INSERT notificaciones ON")
            cursor.execute(
                "INSERT INTO notificaciones (id_notificacion, id_usuario, mensaje, tipo, fecha, leido, prioridad) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                entidad.id_notificacion,
                entidad.id_usuario,
                entidad.mensaje,
                entidad.tipo.value,
                entidad.fecha,
                entidad.leido,
                entidad.prioridad.value if entidad.prioridad else None,
            )
            cursor.execute("SET IDENTITY_INSERT notificaciones OFF")
            conexion.commit()
        finally:
            conexion.close()
        return entidad

    def obtener_por_id(self, id_entidad: int) -> Notificacion:
        if not self._usa_sql:
            return super().obtener_por_id(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_notificacion, mensaje, tipo, fecha, leido, id_usuario, prioridad "
                "FROM notificaciones WHERE id_notificacion = ?",
                id_entidad,
            )
            fila = cursor.fetchone()
            if fila is None:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            return self._fila_a_notificacion(fila)
        finally:
            conexion.close()

    def existe(self, id_entidad: int) -> bool:
        if not self._usa_sql:
            return super().existe(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 FROM notificaciones WHERE id_notificacion = ?", id_entidad)
            return cursor.fetchone() is not None
        finally:
            conexion.close()

    def listar(self) -> list[Notificacion]:
        if not self._usa_sql:
            return super().listar()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_notificacion, mensaje, tipo, fecha, leido, id_usuario, prioridad FROM notificaciones"
            )
            return [self._fila_a_notificacion(fila) for fila in cursor.fetchall()]
        finally:
            conexion.close()

    def actualizar(self, entidad: Notificacion) -> Notificacion:
        if not self._usa_sql:
            return super().actualizar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE notificaciones SET mensaje = ?, leido = ? WHERE id_notificacion = ?",
                entidad.mensaje,
                entidad.leido,
                entidad.id_notificacion,
            )
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, entidad.id_notificacion)
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
            cursor.execute("DELETE FROM notificaciones WHERE id_notificacion = ?", id_entidad)
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            conexion.commit()
        finally:
            conexion.close()

    def listar_no_leidas(self) -> list[Notificacion]:
        return [n for n in self.listar() if not n.leido]

    def listar_por_usuario(self, id_usuario: int, solo_no_leidas: bool = False) -> list[Notificacion]:
        notificaciones = [n for n in self.listar() if n.id_usuario == id_usuario]
        if solo_no_leidas:
            notificaciones = [n for n in notificaciones if not n.leido]
        return notificaciones

    @staticmethod
    def _fila_a_notificacion(fila) -> Notificacion:
        return Notificacion(
            id_notificacion=fila[0],
            mensaje=fila[1],
            tipo=TipoNotificacionEnum(fila[2]),
            fecha=fila[3],
            leido=bool(fila[4]),
            id_usuario=fila[5],
            prioridad=PrioridadEnum(fila[6]) if fila[6] else None,
        )
