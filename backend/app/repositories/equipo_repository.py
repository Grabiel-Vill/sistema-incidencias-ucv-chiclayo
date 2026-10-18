from app.config.database import DatabaseConnection
from app.exceptions import RecursoNoEncontradoException
from app.models.enums import EstadoEquipoEnum
from app.models.equipo import Equipo
from app.repositories.base_repository import BaseRepository


class EquipoRepository(BaseRepository[Equipo, int]):
    """Persistencia de Equipo. `entidad.id_laboratorio` ya viene poblado por
    Laboratorio.agregar_equipo() antes de que el servicio llame a agregar()."""

    def __init__(self, database: DatabaseConnection | None = None):
        super().__init__(nombre_entidad="Equipo", database=database)

    def _obtener_id(self, entidad: Equipo) -> int:
        return entidad.id_equipo

    def siguiente_id(self) -> int:
        if not self._usa_sql:
            return super().siguiente_id()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ISNULL(MAX(id_equipo), 0) + 1 FROM equipos")
            return cursor.fetchone()[0]
        finally:
            conexion.close()

    def agregar(self, entidad: Equipo) -> Equipo:
        if not self._usa_sql:
            return super().agregar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SET IDENTITY_INSERT equipos ON")
            cursor.execute(
                "INSERT INTO equipos (id_equipo, id_laboratorio, codigo_patrimonial, tipo_equipo, estado) "
                "VALUES (?, ?, ?, ?, ?)",
                entidad.id_equipo,
                entidad.id_laboratorio,
                entidad.codigo_patrimonial,
                entidad.tipo_equipo,
                entidad.estado.value,
            )
            cursor.execute("SET IDENTITY_INSERT equipos OFF")
            conexion.commit()
        finally:
            conexion.close()
        return entidad

    def obtener_por_id(self, id_entidad: int) -> Equipo:
        if not self._usa_sql:
            return super().obtener_por_id(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_equipo, codigo_patrimonial, tipo_equipo, estado, id_laboratorio "
                "FROM equipos WHERE id_equipo = ?",
                id_entidad,
            )
            fila = cursor.fetchone()
            if fila is None:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            return self._fila_a_equipo(fila)
        finally:
            conexion.close()

    def existe(self, id_entidad: int) -> bool:
        if not self._usa_sql:
            return super().existe(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 FROM equipos WHERE id_equipo = ?", id_entidad)
            return cursor.fetchone() is not None
        finally:
            conexion.close()

    def listar(self) -> list[Equipo]:
        if not self._usa_sql:
            return super().listar()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_equipo, codigo_patrimonial, tipo_equipo, estado, id_laboratorio FROM equipos")
            return [self._fila_a_equipo(fila) for fila in cursor.fetchall()]
        finally:
            conexion.close()

    def actualizar(self, entidad: Equipo) -> Equipo:
        if not self._usa_sql:
            return super().actualizar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE equipos SET codigo_patrimonial = ?, tipo_equipo = ?, estado = ? WHERE id_equipo = ?",
                entidad.codigo_patrimonial,
                entidad.tipo_equipo,
                entidad.estado.value,
                entidad.id_equipo,
            )
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, entidad.id_equipo)
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
            cursor.execute("DELETE FROM equipos WHERE id_equipo = ?", id_entidad)
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            conexion.commit()
        finally:
            conexion.close()

    def buscar_por_codigo_patrimonial(self, codigo_patrimonial: str) -> Equipo | None:
        return next((e for e in self.listar() if e.codigo_patrimonial == codigo_patrimonial), None)

    def listar_por_estado(self, estado: EstadoEquipoEnum) -> list[Equipo]:
        return [e for e in self.listar() if e.estado == estado]

    @staticmethod
    def _fila_a_equipo(fila) -> Equipo:
        equipo = Equipo(
            id_equipo=fila[0],
            codigo_patrimonial=fila[1],
            tipo_equipo=fila[2],
            estado=EstadoEquipoEnum(fila[3]),
        )
        equipo.asociar_laboratorio(fila[4])
        return equipo
