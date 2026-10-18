from app.config.database import DatabaseConnection
from app.exceptions import RecursoNoEncontradoException
from app.models.evidencia import Evidencia
from app.repositories.base_repository import BaseRepository


class EvidenciaRepository(BaseRepository[Evidencia, int]):
    """Persistencia de Evidencia fotografica. `entidad.id_incidencia` ya viene poblado por
    Incidencia.agregar_evidencia() antes de que el servicio llame a agregar()."""

    def __init__(self, database: DatabaseConnection | None = None):
        super().__init__(nombre_entidad="Evidencia", database=database)

    def _obtener_id(self, entidad: Evidencia) -> int:
        return entidad.id_evidencia

    def siguiente_id(self) -> int:
        if not self._usa_sql:
            return super().siguiente_id()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ISNULL(MAX(id_evidencia), 0) + 1 FROM evidencias")
            return cursor.fetchone()[0]
        finally:
            conexion.close()

    def agregar(self, entidad: Evidencia) -> Evidencia:
        if not self._usa_sql:
            return super().agregar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SET IDENTITY_INSERT evidencias ON")
            cursor.execute(
                "INSERT INTO evidencias (id_evidencia, id_incidencia, url_imagen, fecha_carga) "
                "VALUES (?, ?, ?, ?)",
                entidad.id_evidencia,
                entidad.id_incidencia,
                entidad.url_imagen,
                entidad.fecha_carga,
            )
            cursor.execute("SET IDENTITY_INSERT evidencias OFF")
            conexion.commit()
        finally:
            conexion.close()
        return entidad

    def obtener_por_id(self, id_entidad: int) -> Evidencia:
        if not self._usa_sql:
            return super().obtener_por_id(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_evidencia, url_imagen, fecha_carga, id_incidencia FROM evidencias WHERE id_evidencia = ?",
                id_entidad,
            )
            fila = cursor.fetchone()
            if fila is None:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            return self._fila_a_evidencia(fila)
        finally:
            conexion.close()

    def existe(self, id_entidad: int) -> bool:
        if not self._usa_sql:
            return super().existe(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 FROM evidencias WHERE id_evidencia = ?", id_entidad)
            return cursor.fetchone() is not None
        finally:
            conexion.close()

    def listar(self) -> list[Evidencia]:
        if not self._usa_sql:
            return super().listar()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_evidencia, url_imagen, fecha_carga, id_incidencia FROM evidencias")
            return [self._fila_a_evidencia(fila) for fila in cursor.fetchall()]
        finally:
            conexion.close()

    def actualizar(self, entidad: Evidencia) -> Evidencia:
        if not self._usa_sql:
            return super().actualizar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE evidencias SET url_imagen = ? WHERE id_evidencia = ?",
                entidad.url_imagen,
                entidad.id_evidencia,
            )
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, entidad.id_evidencia)
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
            cursor.execute("DELETE FROM evidencias WHERE id_evidencia = ?", id_entidad)
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            conexion.commit()
        finally:
            conexion.close()

    def listar_por_incidencia(self, id_incidencia: int) -> list[Evidencia]:
        return [e for e in self.listar() if e.id_incidencia == id_incidencia]

    @staticmethod
    def _fila_a_evidencia(fila) -> Evidencia:
        evidencia = Evidencia(id_evidencia=fila[0], url_imagen=fila[1], fecha_carga=fila[2])
        evidencia.asociar_incidencia(fila[3])
        return evidencia
