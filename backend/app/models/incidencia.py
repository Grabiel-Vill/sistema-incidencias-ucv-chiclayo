from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from app.exceptions import TransicionEstadoInvalidaException, ValidacionException
from app.models.enums import EstadoIncidenciaEnum, PrioridadEnum, TipoFallaEnum, TipoRequerimientoEnum
from app.models.equipo import Equipo
from app.models.evidencia import Evidencia
from app.models.laboratorio import Laboratorio
from app.models.nota_tecnica import NotaTecnica
from app.models.tecnico import Tecnico
from app.utils.ticket_code_generator import TicketCodeGenerator

if TYPE_CHECKING:
    from app.models.docente import Docente

_TRANSICIONES_VALIDAS: dict[EstadoIncidenciaEnum, set[EstadoIncidenciaEnum]] = {
    EstadoIncidenciaEnum.RECIBIDO: {EstadoIncidenciaEnum.PROGRAMADO, EstadoIncidenciaEnum.EN_PROCESO},
    EstadoIncidenciaEnum.PROGRAMADO: {EstadoIncidenciaEnum.EN_PROCESO, EstadoIncidenciaEnum.RESUELTO},
    EstadoIncidenciaEnum.EN_PROCESO: {EstadoIncidenciaEnum.RESUELTO},
    EstadoIncidenciaEnum.RESUELTO: set(),
}


class Incidencia:
    """Falla tecnica o solicitud de apertura anticipada reportada sobre un Laboratorio (RF1)."""

    def __init__(
        self,
        id_incidencia: int,
        codigo_ticket: str,
        descripcion: str,
        tipo_falla: TipoFallaEnum | None,
        laboratorio: Laboratorio,
        docente: "Docente",
        tipo_requerimiento: TipoRequerimientoEnum = TipoRequerimientoEnum.FALLA_TECNICA,
        equipo: Equipo | None = None,
        prioridad: PrioridadEnum = PrioridadEnum.MEDIA,
        fecha_hora_apertura: datetime | None = None,
        fecha_creacion: datetime | None = None,
        subcategoria: str | None = None,
    ):
        self._id_incidencia = id_incidencia
        self._codigo_ticket = codigo_ticket
        self.descripcion = descripcion
        self._tipo_falla = tipo_falla
        self.subcategoria = subcategoria
        self._laboratorio = laboratorio
        self._docente = docente
        self._tipo_requerimiento = tipo_requerimiento
        self._equipo = equipo
        self._prioridad = prioridad
        self._fecha_hora_apertura = fecha_hora_apertura
        self._estado = EstadoIncidenciaEnum.RECIBIDO
        self._fecha_creacion = fecha_creacion or datetime.now()
        self._fecha_atencion: datetime | None = None
        self._fecha_resolucion: datetime | None = None
        self._tecnico_asignado: Tecnico | None = None
        self._evidencias: list[Evidencia] = []
        self._notas_tecnicas: list[NotaTecnica] = []

    @classmethod
    def crear(
        cls,
        id_incidencia: int,
        descripcion: str,
        tipo_falla: TipoFallaEnum | None,
        laboratorio: Laboratorio,
        docente: "Docente",
        tipo_requerimiento: TipoRequerimientoEnum = TipoRequerimientoEnum.FALLA_TECNICA,
        equipo: Equipo | None = None,
        fecha_hora_apertura: datetime | None = None,
        subcategoria: str | None = None,
    ) -> "Incidencia":
        return cls(
            id_incidencia=id_incidencia,
            codigo_ticket=TicketCodeGenerator.generar(id_incidencia),
            descripcion=descripcion,
            tipo_falla=tipo_falla,
            laboratorio=laboratorio,
            docente=docente,
            tipo_requerimiento=tipo_requerimiento,
            equipo=equipo,
            fecha_hora_apertura=fecha_hora_apertura,
            subcategoria=subcategoria,
        )

    @classmethod
    def reconstruir(
        cls,
        id_incidencia: int,
        codigo_ticket: str,
        descripcion: str,
        tipo_falla: TipoFallaEnum | None,
        laboratorio: Laboratorio,
        docente: "Docente",
        estado: EstadoIncidenciaEnum,
        prioridad: PrioridadEnum,
        fecha_creacion: datetime,
        tipo_requerimiento: TipoRequerimientoEnum = TipoRequerimientoEnum.FALLA_TECNICA,
        equipo: Equipo | None = None,
        fecha_hora_apertura: datetime | None = None,
        fecha_atencion: datetime | None = None,
        fecha_resolucion: datetime | None = None,
        tecnico_asignado: Tecnico | None = None,
        subcategoria: str | None = None,
    ) -> "Incidencia":
        """Reconstruye una Incidencia ya existente (ej. desde la base de datos) preservando su
        estado real, a diferencia de `crear()` que siempre arranca un ticket nuevo en RECIBIDO."""
        incidencia = cls(
            id_incidencia=id_incidencia,
            codigo_ticket=codigo_ticket,
            descripcion=descripcion,
            tipo_falla=tipo_falla,
            laboratorio=laboratorio,
            docente=docente,
            tipo_requerimiento=tipo_requerimiento,
            equipo=equipo,
            prioridad=prioridad,
            fecha_hora_apertura=fecha_hora_apertura,
            fecha_creacion=fecha_creacion,
            subcategoria=subcategoria,
        )
        incidencia._estado = estado
        incidencia._fecha_atencion = fecha_atencion
        incidencia._fecha_resolucion = fecha_resolucion
        incidencia._tecnico_asignado = tecnico_asignado
        return incidencia

    @property
    def id_incidencia(self) -> int:
        return self._id_incidencia

    @property
    def codigo_ticket(self) -> str:
        return self._codigo_ticket

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValidacionException("La descripcion no puede estar vacia", campo="descripcion")
        self._descripcion = valor.strip()

    @property
    def tipo_falla(self) -> TipoFallaEnum | None:
        return self._tipo_falla

    @property
    def subcategoria(self) -> str | None:
        return self._subcategoria

    @subcategoria.setter
    def subcategoria(self, valor: str | None) -> None:
        if valor is not None and not valor.strip():
            raise ValidacionException("La subcategoria no puede estar vacia", campo="subcategoria")
        self._subcategoria = valor.strip() if valor else None

    @property
    def tipo_requerimiento(self) -> TipoRequerimientoEnum:
        return self._tipo_requerimiento

    @property
    def laboratorio(self) -> Laboratorio:
        return self._laboratorio

    @property
    def docente(self) -> "Docente":
        return self._docente

    @property
    def equipo(self) -> Equipo | None:
        return self._equipo

    @property
    def estado(self) -> EstadoIncidenciaEnum:
        return self._estado

    @property
    def prioridad(self) -> PrioridadEnum:
        return self._prioridad

    @prioridad.setter
    def prioridad(self, valor: PrioridadEnum) -> None:
        self._prioridad = valor

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    @property
    def fecha_atencion(self) -> datetime | None:
        return self._fecha_atencion

    @property
    def fecha_resolucion(self) -> datetime | None:
        return self._fecha_resolucion

    @property
    def fecha_hora_apertura(self) -> datetime | None:
        return self._fecha_hora_apertura

    @property
    def tecnico_asignado(self) -> Tecnico | None:
        return self._tecnico_asignado

    @property
    def evidencias(self) -> list[Evidencia]:
        return list(self._evidencias)

    @property
    def notas_tecnicas(self) -> list[NotaTecnica]:
        return list(self._notas_tecnicas)

    def cambiar_estado(self, nuevo_estado: EstadoIncidenciaEnum) -> None:
        if nuevo_estado not in _TRANSICIONES_VALIDAS[self._estado]:
            raise TransicionEstadoInvalidaException(self._estado, nuevo_estado)
        self._estado = nuevo_estado
        if nuevo_estado == EstadoIncidenciaEnum.EN_PROCESO and self._fecha_atencion is None:
            self._fecha_atencion = datetime.now()
        elif nuevo_estado == EstadoIncidenciaEnum.RESUELTO:
            self._fecha_resolucion = datetime.now()

    def asignar_tecnico(self, tecnico: Tecnico) -> None:
        if not isinstance(tecnico, Tecnico):
            raise ValidacionException("Solo un Tecnico puede ser asignado a una Incidencia", campo="tecnico")
        self._tecnico_asignado = tecnico

    def calcular_tiempo_atencion(self) -> timedelta | None:
        if self._fecha_atencion is None:
            return None
        return self._fecha_atencion - self._fecha_creacion

    def calcular_tiempo_resolucion(self) -> timedelta | None:
        if self._fecha_resolucion is None:
            return None
        return self._fecha_resolucion - self._fecha_creacion

    # --- Composicion: la Evidencia y la NotaTecnica viven dentro de la Incidencia ---

    def agregar_evidencia(self, evidencia: Evidencia) -> None:
        evidencia.asociar_incidencia(self._id_incidencia)
        self._evidencias.append(evidencia)

    def agregar_nota_tecnica(self, nota: NotaTecnica) -> None:
        nota.asociar_incidencia(self._id_incidencia)
        self._notas_tecnicas.append(nota)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Incidencia) and self._id_incidencia == other._id_incidencia

    def __hash__(self) -> int:
        return hash(self._id_incidencia)

    def __repr__(self) -> str:
        return f"Incidencia(ticket='{self._codigo_ticket}', estado={self._estado.value})"
