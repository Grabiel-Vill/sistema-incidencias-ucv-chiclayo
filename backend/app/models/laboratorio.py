from __future__ import annotations

from typing import TYPE_CHECKING

from app.exceptions import ValidacionException
from app.models.equipo import Equipo

if TYPE_CHECKING:
    from app.models.incidencia import Incidencia


class Laboratorio:
    """Laboratorio informatico. Agrega 0..* Equipo (los equipos pueden existir/reasignarse aparte)."""

    def __init__(
        self,
        id_laboratorio: int,
        nombre: str,
        pabellon: str,
        piso: int,
        estado_operativo: bool = True,
    ):
        self._id_laboratorio = id_laboratorio
        self.nombre = nombre
        self.pabellon = pabellon
        self.piso = piso
        self._estado_operativo = estado_operativo
        self._equipos: list[Equipo] = []

    @property
    def id_laboratorio(self) -> int:
        return self._id_laboratorio

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValidacionException("El nombre del laboratorio no puede estar vacio", campo="nombre")
        self._nombre = valor.strip()

    @property
    def pabellon(self) -> str:
        return self._pabellon

    @pabellon.setter
    def pabellon(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValidacionException("El pabellon no puede estar vacio", campo="pabellon")
        self._pabellon = valor.strip()

    @property
    def piso(self) -> int:
        return self._piso

    @piso.setter
    def piso(self, valor: int) -> None:
        if valor < 0:
            raise ValidacionException("El piso no puede ser negativo", campo="piso")
        self._piso = valor

    @property
    def estado_operativo(self) -> bool:
        return self._estado_operativo

    def actualizar_estado_operativo(self, operativo: bool) -> None:
        self._estado_operativo = operativo

    # --- Agregacion: Laboratorio 1 -- 0..* Equipo ---

    @property
    def equipos(self) -> list[Equipo]:
        return list(self._equipos)

    def agregar_equipo(self, equipo: Equipo) -> None:
        if equipo not in self._equipos:
            equipo.asociar_laboratorio(self._id_laboratorio)
            self._equipos.append(equipo)

    def retirar_equipo(self, equipo: Equipo) -> None:
        if equipo in self._equipos:
            self._equipos.remove(equipo)

    def obtener_historial_incidencias(self, incidencias: list["Incidencia"]) -> list["Incidencia"]:
        return [incidencia for incidencia in incidencias if incidencia.laboratorio == self]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Laboratorio) and self._id_laboratorio == other._id_laboratorio

    def __hash__(self) -> int:
        return hash(self._id_laboratorio)

    def __repr__(self) -> str:
        return f"Laboratorio(id={self._id_laboratorio}, nombre='{self._nombre}', pabellon='{self._pabellon}')"
