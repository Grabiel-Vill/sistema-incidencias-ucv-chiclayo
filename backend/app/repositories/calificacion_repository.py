from app.config.database import DatabaseConnection
from app.exceptions import RecursoNoEncontradoException
from app.models.calificacion import Calificacion
from app.repositories.base_repository import BaseRepository

_SELECT_CALIFICACIONES = (
    "SELECT id_calificacion, id_incidencia, id_docente, id_tecnico, estrellas, comentario, fecha "
    "FROM calificaciones"
)


class CalificacionRepository(BaseRepository[Calificacion, int]):
    """Persistencia de Calificacion (una por incidencia) y consultas de promedio para el dashboard."""

    def __init__(self, database: DatabaseConnection | None = None):
        super().__init__(nombre_entidad="Calificacion", database=database)

    def _obtener_id(self, entidad: Calificacion) -> int:
        return entidad.id_calificacion

    def siguiente_id(self) -> int:
        if not self._usa_sql:
            return super().siguiente_id()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ISNULL(MAX(id_calificacion), 0) + 1 FROM calificaciones")
            return cursor.fetchone()[0]
        finally:
            conexion.close()

    def agregar(self, entidad: Calificacion) -> Calificacion:
        if not self._usa_sql:
            return super().agregar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SET IDENTITY_INSERT calificaciones ON")
            cursor.execute(
                "INSERT INTO calificaciones (id_calificacion, id_incidencia, id_docente, id_tecnico, "
                "estrellas, comentario, fecha) VALUES (?, ?, ?, ?, ?, ?, ?)",
                entidad.id_calificacion,
                entidad.id_incidencia,
                entidad.id_docente,
                entidad.id_tecnico,
                entidad.estrellas,
                entidad.comentario,
                entidad.fecha,
            )
            cursor.execute("SET IDENTITY_INSERT calificaciones OFF")
            conexion.commit()
        finally:
            conexion.close()
        return entidad

    def obtener_por_id(self, id_entidad: int) -> Calificacion:
        if not self._usa_sql:
            return super().obtener_por_id(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"{_SELECT_CALIFICACIONES} WHERE id_calificacion = ?", id_entidad)
            fila = cursor.fetchone()
            if fila is None:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            return self._fila_a_calificacion(fila)
        finally:
            conexion.close()

    def existe(self, id_entidad: int) -> bool:
        if not self._usa_sql:
            return super().existe(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 FROM calificaciones WHERE id_calificacion = ?", id_entidad)
            return cursor.fetchone() is not None
        finally:
            conexion.close()

    def listar(self) -> list[Calificacion]:
        if not self._usa_sql:
            return super().listar()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(_SELECT_CALIFICACIONES)
            return [self._fila_a_calificacion(fila) for fila in cursor.fetchall()]
        finally:
            conexion.close()

    def eliminar(self, id_entidad: int) -> None:
        if not self._usa_sql:
            return super().eliminar(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM calificaciones WHERE id_calificacion = ?", id_entidad)
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            conexion.commit()
        finally:
            conexion.close()

    def buscar_por_incidencia(self, id_incidencia: int) -> Calificacion | None:
        return next((c for c in self.listar() if c.id_incidencia == id_incidencia), None)

    def promedio_estrellas(self) -> float | None:
        calificaciones = self.listar()
        if not calificaciones:
            return None
        return sum(c.estrellas for c in calificaciones) / len(calificaciones)

    @staticmethod
    def _fila_a_calificacion(fila) -> Calificacion:
        return Calificacion(
            id_calificacion=fila[0],
            id_incidencia=fila[1],
            id_docente=fila[2],
            id_tecnico=fila[3],
            estrellas=fila[4],
            comentario=fila[5],
            fecha=fila[6],
        )
