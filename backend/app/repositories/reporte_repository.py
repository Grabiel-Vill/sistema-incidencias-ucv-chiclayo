from app.config.database import DatabaseConnection
from app.exceptions import RecursoNoEncontradoException
from app.models.reporte import Reporte
from app.repositories.base_repository import BaseRepository


class ReporteRepository(BaseRepository[Reporte, int]):
    """Historial de reportes de mantenimiento generados (RF5). Solo persiste id+fecha: los
    KPIs/frecuencia de fallas se recalculan desde IncidenciaRepository cada vez que se piden."""

    def __init__(self, database: DatabaseConnection | None = None):
        super().__init__(nombre_entidad="Reporte", database=database)

    def _obtener_id(self, entidad: Reporte) -> int:
        return entidad.id_reporte

    def siguiente_id(self) -> int:
        if not self._usa_sql:
            return super().siguiente_id()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ISNULL(MAX(id_reporte), 0) + 1 FROM reportes")
            return cursor.fetchone()[0]
        finally:
            conexion.close()

    def agregar(self, entidad: Reporte) -> Reporte:
        if not self._usa_sql:
            return super().agregar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SET IDENTITY_INSERT reportes ON")
            cursor.execute(
                "INSERT INTO reportes (id_reporte, fecha_generacion) VALUES (?, ?)",
                entidad.id_reporte,
                entidad.fecha_generacion,
            )
            cursor.execute("SET IDENTITY_INSERT reportes OFF")
            conexion.commit()
        finally:
            conexion.close()
        return entidad

    def obtener_por_id(self, id_entidad: int) -> Reporte:
        if not self._usa_sql:
            return super().obtener_por_id(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_reporte, fecha_generacion FROM reportes WHERE id_reporte = ?", id_entidad)
            fila = cursor.fetchone()
            if fila is None:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            return Reporte(id_reporte=fila[0], fecha_generacion=fila[1])
        finally:
            conexion.close()

    def existe(self, id_entidad: int) -> bool:
        if not self._usa_sql:
            return super().existe(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 FROM reportes WHERE id_reporte = ?", id_entidad)
            return cursor.fetchone() is not None
        finally:
            conexion.close()

    def listar(self) -> list[Reporte]:
        if not self._usa_sql:
            return super().listar()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_reporte, fecha_generacion FROM reportes")
            return [Reporte(id_reporte=fila[0], fecha_generacion=fila[1]) for fila in cursor.fetchall()]
        finally:
            conexion.close()

    def actualizar(self, entidad: Reporte) -> Reporte:
        if not self._usa_sql:
            return super().actualizar(entidad)
        raise RecursoNoEncontradoException(self._nombre_entidad, entidad.id_reporte)

    def eliminar(self, id_entidad: int) -> None:
        if not self._usa_sql:
            return super().eliminar(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM reportes WHERE id_reporte = ?", id_entidad)
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            conexion.commit()
        finally:
            conexion.close()

    def listar_mas_recientes(self, limite: int = 10) -> list[Reporte]:
        return sorted(self.listar(), key=lambda r: r.fecha_generacion, reverse=True)[:limite]
