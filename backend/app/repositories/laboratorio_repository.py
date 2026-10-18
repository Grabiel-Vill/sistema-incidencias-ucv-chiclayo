from app.config.database import DatabaseConnection
from app.exceptions import RecursoNoEncontradoException
from app.models.enums import EstadoEquipoEnum
from app.models.equipo import Equipo
from app.models.laboratorio import Laboratorio
from app.repositories.base_repository import BaseRepository


class LaboratorioRepository(BaseRepository[Laboratorio, int]):
    """Persistencia de Laboratorio. Al leer desde SQL Server tambien hidrata sus Equipo
    asociados (tabla `equipos`, FK `id_laboratorio`), igual que la composicion en memoria."""

    def __init__(self, database: DatabaseConnection | None = None):
        super().__init__(nombre_entidad="Laboratorio", database=database)

    def _obtener_id(self, entidad: Laboratorio) -> int:
        return entidad.id_laboratorio

    def siguiente_id(self) -> int:
        if not self._usa_sql:
            return super().siguiente_id()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ISNULL(MAX(id_laboratorio), 0) + 1 FROM laboratorios")
            return cursor.fetchone()[0]
        finally:
            conexion.close()

    def agregar(self, entidad: Laboratorio) -> Laboratorio:
        if not self._usa_sql:
            return super().agregar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SET IDENTITY_INSERT laboratorios ON")
            cursor.execute(
                "INSERT INTO laboratorios (id_laboratorio, nombre, pabellon, piso, estado_operativo) "
                "VALUES (?, ?, ?, ?, ?)",
                entidad.id_laboratorio,
                entidad.nombre,
                entidad.pabellon,
                entidad.piso,
                entidad.estado_operativo,
            )
            cursor.execute("SET IDENTITY_INSERT laboratorios OFF")
            conexion.commit()
        finally:
            conexion.close()
        return entidad

    def obtener_por_id(self, id_entidad: int) -> Laboratorio:
        if not self._usa_sql:
            return super().obtener_por_id(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_laboratorio, nombre, pabellon, piso, estado_operativo "
                "FROM laboratorios WHERE id_laboratorio = ?",
                id_entidad,
            )
            fila = cursor.fetchone()
            if fila is None:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            laboratorio = self._fila_a_laboratorio(fila)
            self._hidratar_equipos(cursor, laboratorio)
            return laboratorio
        finally:
            conexion.close()

    def existe(self, id_entidad: int) -> bool:
        if not self._usa_sql:
            return super().existe(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 FROM laboratorios WHERE id_laboratorio = ?", id_entidad)
            return cursor.fetchone() is not None
        finally:
            conexion.close()

    def listar(self) -> list[Laboratorio]:
        if not self._usa_sql:
            return super().listar()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_laboratorio, nombre, pabellon, piso, estado_operativo FROM laboratorios")
            laboratorios = [self._fila_a_laboratorio(fila) for fila in cursor.fetchall()]
            for laboratorio in laboratorios:
                self._hidratar_equipos(cursor, laboratorio)
            return laboratorios
        finally:
            conexion.close()

    def actualizar(self, entidad: Laboratorio) -> Laboratorio:
        if not self._usa_sql:
            return super().actualizar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE laboratorios SET nombre = ?, pabellon = ?, piso = ?, estado_operativo = ? "
                "WHERE id_laboratorio = ?",
                entidad.nombre,
                entidad.pabellon,
                entidad.piso,
                entidad.estado_operativo,
                entidad.id_laboratorio,
            )
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, entidad.id_laboratorio)
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
            cursor.execute("DELETE FROM laboratorios WHERE id_laboratorio = ?", id_entidad)
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            conexion.commit()
        finally:
            conexion.close()

    def buscar_por_pabellon(self, pabellon: str) -> list[Laboratorio]:
        return [lab for lab in self.listar() if lab.pabellon == pabellon]

    def listar_operativos(self) -> list[Laboratorio]:
        return [lab for lab in self.listar() if lab.estado_operativo]

    def _hidratar_equipos(self, cursor, laboratorio: Laboratorio) -> None:
        cursor.execute(
            "SELECT id_equipo, codigo_patrimonial, tipo_equipo, estado FROM equipos WHERE id_laboratorio = ?",
            laboratorio.id_laboratorio,
        )
        for fila_equipo in cursor.fetchall():
            laboratorio.agregar_equipo(self._fila_a_equipo(fila_equipo))

    @staticmethod
    def _fila_a_laboratorio(fila) -> Laboratorio:
        return Laboratorio(
            id_laboratorio=fila[0],
            nombre=fila[1],
            pabellon=fila[2],
            piso=fila[3],
            estado_operativo=bool(fila[4]),
        )

    @staticmethod
    def _fila_a_equipo(fila) -> Equipo:
        return Equipo(
            id_equipo=fila[0],
            codigo_patrimonial=fila[1],
            tipo_equipo=fila[2],
            estado=EstadoEquipoEnum(fila[3]),
        )
