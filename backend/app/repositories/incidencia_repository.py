from __future__ import annotations

from typing import TYPE_CHECKING

from app.config.database import DatabaseConnection
from app.exceptions import RecursoNoEncontradoException
from app.models.enums import EstadoIncidenciaEnum, PrioridadEnum, TipoFallaEnum, TipoRequerimientoEnum
from app.models.evidencia import Evidencia
from app.models.incidencia import Incidencia
from app.models.nota_tecnica import NotaTecnica
from app.repositories.base_repository import BaseRepository
from app.repositories.laboratorio_repository import LaboratorioRepository
from app.repositories.usuario_repository import UsuarioRepository

if TYPE_CHECKING:
    from app.dtos.filtro_dto import FiltroDTO

_SELECT_INCIDENCIAS = (
    "SELECT id_incidencia, codigo_ticket, descripcion, tipo_falla, tipo_requerimiento, id_laboratorio, "
    "id_equipo, id_docente, id_tecnico_asignado, estado, prioridad, fecha_creacion, fecha_atencion, "
    "fecha_resolucion, fecha_hora_apertura, subcategoria FROM incidencias"
)


class IncidenciaRepository(BaseRepository[Incidencia, int]):
    """CRUD de Incidencia, busqueda por estado/laboratorio/tecnico y consultas para KPIs (RF4, RF5).

    En modo SQL necesita LaboratorioRepository y UsuarioRepository para reconstruir los
    objetos anidados (laboratorio+equipos, docente, tecnico asignado); tambien hidrata
    evidencias/notas_tecnicas porque los servicios las leen desde `incidencia.notas_tecnicas`
    / `incidencia.evidencias`, no desde sus propios repositorios.
    """

    def __init__(
        self,
        database: DatabaseConnection | None = None,
        laboratorio_repository: LaboratorioRepository | None = None,
        usuario_repository: UsuarioRepository | None = None,
    ):
        super().__init__(nombre_entidad="Incidencia", database=database)
        self._laboratorios = laboratorio_repository
        self._usuarios = usuario_repository

    def _obtener_id(self, entidad: Incidencia) -> int:
        return entidad.id_incidencia

    def siguiente_id(self) -> int:
        if not self._usa_sql:
            return super().siguiente_id()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ISNULL(MAX(id_incidencia), 0) + 1 FROM incidencias")
            return cursor.fetchone()[0]
        finally:
            conexion.close()

    def agregar(self, entidad: Incidencia) -> Incidencia:
        if not self._usa_sql:
            return super().agregar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SET IDENTITY_INSERT incidencias ON")
            cursor.execute(
                "INSERT INTO incidencias (id_incidencia, codigo_ticket, descripcion, tipo_falla, "
                "tipo_requerimiento, id_laboratorio, id_equipo, id_docente, id_tecnico_asignado, estado, "
                "prioridad, fecha_creacion, fecha_atencion, fecha_resolucion, fecha_hora_apertura, subcategoria) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                entidad.id_incidencia,
                entidad.codigo_ticket,
                entidad.descripcion,
                entidad.tipo_falla.value if entidad.tipo_falla else None,
                entidad.tipo_requerimiento.value,
                entidad.laboratorio.id_laboratorio,
                entidad.equipo.id_equipo if entidad.equipo else None,
                entidad.docente.id_usuario,
                entidad.tecnico_asignado.id_usuario if entidad.tecnico_asignado else None,
                entidad.estado.value,
                entidad.prioridad.value,
                entidad.fecha_creacion,
                entidad.fecha_atencion,
                entidad.fecha_resolucion,
                entidad.fecha_hora_apertura,
                entidad.subcategoria,
            )
            cursor.execute("SET IDENTITY_INSERT incidencias OFF")
            conexion.commit()
        finally:
            conexion.close()
        return entidad

    def obtener_por_id(self, id_entidad: int) -> Incidencia:
        if not self._usa_sql:
            return super().obtener_por_id(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(f"{_SELECT_INCIDENCIAS} WHERE id_incidencia = ?", id_entidad)
            fila = cursor.fetchone()
            if fila is None:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            incidencia = self._fila_a_incidencia(fila)
            self._hidratar_hijos(cursor, incidencia)
            return incidencia
        finally:
            conexion.close()

    def existe(self, id_entidad: int) -> bool:
        if not self._usa_sql:
            return super().existe(id_entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 FROM incidencias WHERE id_incidencia = ?", id_entidad)
            return cursor.fetchone() is not None
        finally:
            conexion.close()

    def listar(self) -> list[Incidencia]:
        if not self._usa_sql:
            return super().listar()
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(_SELECT_INCIDENCIAS)
            incidencias = [self._fila_a_incidencia(fila) for fila in cursor.fetchall()]

            cursor.execute("SELECT id_evidencia, url_imagen, fecha_carga, id_incidencia FROM evidencias")
            evidencias_por_incidencia: dict[int, list] = {}
            for fila_ev in cursor.fetchall():
                evidencias_por_incidencia.setdefault(fila_ev[3], []).append(fila_ev)

            cursor.execute(
                "SELECT id_nota, contenido, es_privado, fecha_creacion, id_incidencia FROM notas_tecnicas"
            )
            notas_por_incidencia: dict[int, list] = {}
            for fila_nota in cursor.fetchall():
                notas_por_incidencia.setdefault(fila_nota[4], []).append(fila_nota)

            for incidencia in incidencias:
                for fila_ev in evidencias_por_incidencia.get(incidencia.id_incidencia, []):
                    incidencia.agregar_evidencia(self._fila_a_evidencia(fila_ev))
                for fila_nota in notas_por_incidencia.get(incidencia.id_incidencia, []):
                    incidencia.agregar_nota_tecnica(self._fila_a_nota(fila_nota))
            return incidencias
        finally:
            conexion.close()

    def actualizar(self, entidad: Incidencia) -> Incidencia:
        if not self._usa_sql:
            return super().actualizar(entidad)
        conexion = self._db.conectar()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE incidencias SET descripcion = ?, id_equipo = ?, id_tecnico_asignado = ?, estado = ?, "
                "prioridad = ?, fecha_atencion = ?, fecha_resolucion = ?, subcategoria = ? WHERE id_incidencia = ?",
                entidad.descripcion,
                entidad.equipo.id_equipo if entidad.equipo else None,
                entidad.tecnico_asignado.id_usuario if entidad.tecnico_asignado else None,
                entidad.estado.value,
                entidad.prioridad.value,
                entidad.fecha_atencion,
                entidad.fecha_resolucion,
                entidad.subcategoria,
                entidad.id_incidencia,
            )
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, entidad.id_incidencia)
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
            cursor.execute("DELETE FROM incidencias WHERE id_incidencia = ?", id_entidad)
            if cursor.rowcount == 0:
                raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
            conexion.commit()
        finally:
            conexion.close()

    def buscar_por_codigo_ticket(self, codigo_ticket: str) -> Incidencia | None:
        return next((i for i in self.listar() if i.codigo_ticket == codigo_ticket), None)

    def listar_por_estado(self, estado: EstadoIncidenciaEnum) -> list[Incidencia]:
        return [i for i in self.listar() if i.estado == estado]

    def listar_por_laboratorio(self, id_laboratorio: int) -> list[Incidencia]:
        return [i for i in self.listar() if i.laboratorio.id_laboratorio == id_laboratorio]

    def listar_por_tecnico(self, id_tecnico: int) -> list[Incidencia]:
        return [i for i in self.listar() if i.tecnico_asignado and i.tecnico_asignado.id_usuario == id_tecnico]

    def listar_por_docente(self, id_docente: int) -> list[Incidencia]:
        return [i for i in self.listar() if i.docente.id_usuario == id_docente]

    def listar_pendientes(self) -> list[Incidencia]:
        return [i for i in self.listar() if i.estado != EstadoIncidenciaEnum.RESUELTO]

    def listar_con_filtro(self, filtro: "FiltroDTO") -> list[Incidencia]:
        return [i for i in self.listar() if filtro.aplica_a(i)]

    def _fila_a_incidencia(self, fila) -> Incidencia:
        (
            id_incidencia,
            codigo_ticket,
            descripcion,
            tipo_falla,
            tipo_requerimiento,
            id_laboratorio,
            id_equipo,
            id_docente,
            id_tecnico_asignado,
            estado,
            prioridad,
            fecha_creacion,
            fecha_atencion,
            fecha_resolucion,
            fecha_hora_apertura,
            subcategoria,
        ) = fila

        laboratorio = self._laboratorios.obtener_por_id(id_laboratorio)
        equipo = next((e for e in laboratorio.equipos if e.id_equipo == id_equipo), None) if id_equipo else None
        docente = self._usuarios.obtener_por_id(id_docente)
        tecnico_asignado = self._usuarios.obtener_por_id(id_tecnico_asignado) if id_tecnico_asignado else None

        return Incidencia.reconstruir(
            id_incidencia=id_incidencia,
            codigo_ticket=codigo_ticket,
            descripcion=descripcion,
            tipo_falla=TipoFallaEnum(tipo_falla) if tipo_falla else None,
            laboratorio=laboratorio,
            docente=docente,
            estado=EstadoIncidenciaEnum(estado),
            prioridad=PrioridadEnum(prioridad),
            fecha_creacion=fecha_creacion,
            tipo_requerimiento=TipoRequerimientoEnum(tipo_requerimiento),
            equipo=equipo,
            fecha_hora_apertura=fecha_hora_apertura,
            fecha_atencion=fecha_atencion,
            fecha_resolucion=fecha_resolucion,
            tecnico_asignado=tecnico_asignado,
            subcategoria=subcategoria,
        )

    def _hidratar_hijos(self, cursor, incidencia: Incidencia) -> None:
        cursor.execute(
            "SELECT id_evidencia, url_imagen, fecha_carga, id_incidencia FROM evidencias WHERE id_incidencia = ?",
            incidencia.id_incidencia,
        )
        for fila_ev in cursor.fetchall():
            incidencia.agregar_evidencia(self._fila_a_evidencia(fila_ev))

        cursor.execute(
            "SELECT id_nota, contenido, es_privado, fecha_creacion, id_incidencia FROM notas_tecnicas "
            "WHERE id_incidencia = ?",
            incidencia.id_incidencia,
        )
        for fila_nota in cursor.fetchall():
            incidencia.agregar_nota_tecnica(self._fila_a_nota(fila_nota))

    @staticmethod
    def _fila_a_evidencia(fila) -> Evidencia:
        evidencia = Evidencia(id_evidencia=fila[0], url_imagen=fila[1], fecha_carga=fila[2])
        evidencia.asociar_incidencia(fila[3])
        return evidencia

    @staticmethod
    def _fila_a_nota(fila) -> NotaTecnica:
        nota = NotaTecnica(id_nota=fila[0], contenido=fila[1], es_privado=bool(fila[2]), fecha_creacion=fila[3])
        nota.asociar_incidencia(fila[4])
        return nota
