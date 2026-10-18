from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from app.exceptions import RecursoNoEncontradoException

if TYPE_CHECKING:
    from app.config.database import DatabaseConnection

TEntidad = TypeVar("TEntidad")
TId = TypeVar("TId")


class BaseRepository(ABC, Generic[TEntidad, TId]):
    """CRUD generico reutilizable (patron DAO). Almacena las entidades en memoria por id.

    Cada subclase concreta implementa _obtener_id (Template Method) y puede sumar consultas
    propias (buscar_por_x, listar_por_y) sobre el mismo almacen interno.

    Si se inyecta una `database` configurada (ver DatabaseConnection), las subclases que
    sobrescriben agregar/obtener_por_id/listar/actualizar/eliminar/siguiente_id la usan para
    operar contra SQL Server en vez del diccionario en memoria (propiedad `_usa_sql`). Sin
    base de datos configurada, el repositorio sigue funcionando 100% en memoria, igual que
    EmailClient/LLMClient cuando no tienen credenciales: el backend no deja de arrancar.
    """

    def __init__(self, nombre_entidad: str, database: "DatabaseConnection | None" = None):
        self._nombre_entidad = nombre_entidad
        self._db = database
        self._datos: dict[TId, TEntidad] = {}

    @property
    def _usa_sql(self) -> bool:
        return self._db is not None and self._db.esta_configurado

    @abstractmethod
    def _obtener_id(self, entidad: TEntidad) -> TId:
        """Extrae el identificador de la entidad concreta."""

    def agregar(self, entidad: TEntidad) -> TEntidad:
        self._datos[self._obtener_id(entidad)] = entidad
        return entidad

    def obtener_por_id(self, id_entidad: TId) -> TEntidad:
        try:
            return self._datos[id_entidad]
        except KeyError:
            raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad) from None

    def existe(self, id_entidad: TId) -> bool:
        return id_entidad in self._datos

    def listar(self) -> list[TEntidad]:
        return list(self._datos.values())

    def actualizar(self, entidad: TEntidad) -> TEntidad:
        id_entidad = self._obtener_id(entidad)
        if id_entidad not in self._datos:
            raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
        self._datos[id_entidad] = entidad
        return entidad

    def eliminar(self, id_entidad: TId) -> None:
        if id_entidad not in self._datos:
            raise RecursoNoEncontradoException(self._nombre_entidad, id_entidad)
        del self._datos[id_entidad]

    def siguiente_id(self) -> int:
        """Genera un id autoincremental simple mientras no exista autoincrement de MySQL."""
        return max(self._datos.keys(), default=0) + 1

    def __len__(self) -> int:
        return len(self._datos)
