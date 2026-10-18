from __future__ import annotations

from app.exceptions import TransicionEstadoInvalidaException, ValidacionException
from app.models.enums import EstadoEquipoEnum

_TRANSICIONES_VALIDAS: dict[EstadoEquipoEnum, set[EstadoEquipoEnum]] = {
    EstadoEquipoEnum.OPERATIVO: {EstadoEquipoEnum.DEFECTUOSO, EstadoEquipoEnum.EN_MANTENIMIENTO},
    EstadoEquipoEnum.DEFECTUOSO: {EstadoEquipoEnum.EN_MANTENIMIENTO},
    EstadoEquipoEnum.EN_MANTENIMIENTO: {EstadoEquipoEnum.OPERATIVO, EstadoEquipoEnum.DEFECTUOSO},
}


class Equipo:
    """Equipo fisico de un Laboratorio (PC, proyector, switch, etc.)."""

    def __init__(
        self,
        id_equipo: int,
        codigo_patrimonial: str,
        tipo_equipo: str,
        estado: EstadoEquipoEnum = EstadoEquipoEnum.OPERATIVO,
    ):
        self._id_equipo = id_equipo
        self.codigo_patrimonial = codigo_patrimonial
        self.tipo_equipo = tipo_equipo
        self._estado = estado
        self._id_laboratorio: int | None = None

    @property
    def id_equipo(self) -> int:
        return self._id_equipo

    @property
    def codigo_patrimonial(self) -> str:
        return self._codigo_patrimonial

    @codigo_patrimonial.setter
    def codigo_patrimonial(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValidacionException("El codigo patrimonial no puede estar vacio", campo="codigo_patrimonial")
        self._codigo_patrimonial = valor.strip()

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    @tipo_equipo.setter
    def tipo_equipo(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValidacionException("El tipo de equipo no puede estar vacio", campo="tipo_equipo")
        self._tipo_equipo = valor.strip()

    @property
    def estado(self) -> EstadoEquipoEnum:
        return self._estado

    def cambiar_estado(self, nuevo_estado: EstadoEquipoEnum) -> None:
        if nuevo_estado not in _TRANSICIONES_VALIDAS[self._estado]:
            raise TransicionEstadoInvalidaException(self._estado, nuevo_estado)
        self._estado = nuevo_estado

    def esta_operativo(self) -> bool:
        return self._estado == EstadoEquipoEnum.OPERATIVO

    @property
    def id_laboratorio(self) -> int | None:
        return self._id_laboratorio

    def asociar_laboratorio(self, id_laboratorio: int) -> None:
        self._id_laboratorio = id_laboratorio

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Equipo) and self._id_equipo == other._id_equipo

    def __hash__(self) -> int:
        return hash(self._id_equipo)

    def __repr__(self) -> str:
        return f"Equipo(id={self._id_equipo}, codigo='{self._codigo_patrimonial}', estado={self._estado.value})"
