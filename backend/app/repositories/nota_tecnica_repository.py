from app.config.database import DatabaseConnection
from app.exceptions import RecursoNoEncontradoException
from app.models.nota_tecnica import NotaTecnica
from app.repositories.base_repository import BaseRepository


class NotaTecnicaRepository(BaseRepository[NotaTecnica, int]):
    """Persistencia de NotaTecnica. `entidad.id_incidencia` ya viene poblado por
    Incidencia.agregar_nota_tecnica() antes de que el servicio llame a agregar()."""

    def __init__(self, database: DatabaseConnection | None = None):
        super().__init__(nombre_entidad="NotaTecnica", database=database)

    def _obtener_id(self, entidad: NotaTecnica) -> int:
        return entidad.id_nota

    def siguiente_id(self) -> int:
        if not self._usa_sql:
            return super().siguiente_id()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ISNULL(MAX(id_nota), 0) + 1 FROM notas_tecnicas")
            return cursor.fetchone()[0]
        finally:
            conexion.close()

    def agregar(self, entidad: NotaTecnica) -> NotaTecnica:
        if not self._usa_sql:
            return super().agregar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SET IDENTITY_INSERT notas_tecnicas ON")
            cursor.execute(
                "INSERT INTO notas_tecnicas (id_nota, id_incidencia, contenido, es_privado, fecha_creacion) "
                "VALUES (?, ?, ?, ?, ?)",
                entidad.id_nota,
                entidad.id_incidencia,
                entidad.contenido,
                entidad.es_privado,
                entidad.fecha_creacion,
            )
            cursor.execute("SET IDENTITY_INSERT notas_tecnicas OFF")
            conexion.commit()
        finally:
            conexion.close()
        return entidad

    def obtener_por_id(self, id_entidad: int) -> NotaTecnica:
        if not self._usa_sql:
            return super().obtener_por_id(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_nota, contenido, es_privado, fecha_creacion, id_incidencia "
                "FROM notas_tecnicas WHERE id_nota = ?",
                id_entidad,
            )
            fila = cursor.fetchone()
            if fila is None:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            return self._fila_a_nota(fila)
        finally:
            conexion.close()

    def existe(self, id_entidad: int) -> bool:
        if not self._usa_sql:
            return super().existe(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 FROM notas_tecnicas WHERE id_nota = ?", id_entidad)
            return cursor.fetchone() is not None
        finally:
            conexion.close()

    def listar(self) -> list[NotaTecnica]:
        if not self._usa_sql:
            return super().listar()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_nota, contenido, es_privado, fecha_creacion, id_incidencia FROM notas_tecnicas")
            return [self._fila_a_nota(fila) for fila in cursor.fetchall()]
        finally:
            conexion.close()

    def actualizar(self, entidad: NotaTecnica) -> NotaTecnica:
        if not self._usa_sql:
            return super().actualizar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE notas_tecnicas SET contenido = ?, es_privado = ? WHERE id_nota = ?",
                entidad.contenido,
                entidad.es_privado,
                entidad.id_nota,
            )
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, entidad.id_nota)
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
            cursor.execute("DELETE FROM notas_tecnicas WHERE id_nota = ?", id_entidad)
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            conexion.commit()
        finally:
            conexion.close()

    def listar_publicas(self) -> list[NotaTecnica]:
        return [nota for nota in self.listar() if not nota.es_privado]

    def listar_por_incidencia(self, id_incidencia: int) -> list[NotaTecnica]:
        return [nota for nota in self.listar() if nota.id_incidencia == id_incidencia]

    @staticmethod
    def _fila_a_nota(fila) -> NotaTecnica:
        nota = NotaTecnica(id_nota=fila[0], contenido=fila[1], es_privado=bool(fila[2]), fecha_creacion=fila[3])
        nota.asociar_incidencia(fila[4])
        return nota
