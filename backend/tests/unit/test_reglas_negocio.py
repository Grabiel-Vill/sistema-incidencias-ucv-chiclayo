"""Pruebas de las reglas de negocio nuevas, contra el repositorio EN MEMORIA (sin SQL Server).

Script simple sin dependencias nuevas (no se agrego pytest): cada funcion test_* se ejecuta y
reporta PASO/FALLO. Correr con: python tests/unit/test_reglas_negocio.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.dtos.incidencia_dto import IncidenciaDTO
from app.exceptions import AccesoDenegadoException, ValidacionException
from app.models.administrador import Administrador
from app.models.docente import Docente
from app.models.enums import EstadoIncidenciaEnum, PrioridadEnum, TipoFallaEnum, TipoRequerimientoEnum
from app.models.laboratorio import Laboratorio
from app.models.tecnico import Tecnico
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.equipo_repository import EquipoRepository
from app.repositories.incidencia_repository import IncidenciaRepository
from app.repositories.laboratorio_repository import LaboratorioRepository
from app.repositories.nota_tecnica_repository import NotaTecnicaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.services.calificacion_service import CalificacionService
from app.services.incidencia_service import IncidenciaService
from app.services.nota_tecnica_service import NotaTecnicaService


def _construir_entorno():
    """Arma servicios + repos 100% en memoria (sin pasar DatabaseConnection => _usa_sql=False)."""
    laboratorio_repo = LaboratorioRepository()
    usuario_repo = UsuarioRepository()
    equipo_repo = EquipoRepository()
    incidencia_repo = IncidenciaRepository(laboratorio_repository=laboratorio_repo, usuario_repository=usuario_repo)
    nota_repo = NotaTecnicaRepository()
    calificacion_repo = CalificacionRepository()

    incidencia_service = IncidenciaService(
        incidencia_repo, laboratorio_repo, equipo_repo, notificacion_service=None,
        nota_tecnica_repository=nota_repo, calificacion_repository=calificacion_repo,
    )
    nota_tecnica_service = NotaTecnicaService(nota_repo, incidencia_repo)
    calificacion_service = CalificacionService(calificacion_repo, incidencia_repo)

    laboratorio = Laboratorio(id_laboratorio=1, nombre="Lab Pruebas", pabellon="A", piso=1)
    laboratorio_repo.agregar(laboratorio)

    docente = Docente(1, "D001", "Ana", "Lopez", "ana@ucv.edu.pe", "hash")
    otro_docente = Docente(2, "D002", "Beto", "Cruz", "beto@ucv.edu.pe", "hash")
    tecnico = Tecnico(3, "T001", "Luis", "Perez", "luis@ucv.edu.pe", "hash", especialidad="Redes")
    administrador = Administrador(4, "A001", "Admin", "UCV", "admin@ucv.edu.pe", "hash")
    for usuario in (docente, otro_docente, tecnico, administrador):
        usuario_repo.agregar(usuario)

    return {
        "incidencia_service": incidencia_service,
        "nota_tecnica_service": nota_tecnica_service,
        "calificacion_service": calificacion_service,
        "docente": docente,
        "otro_docente": otro_docente,
        "tecnico": tecnico,
        "administrador": administrador,
    }


def test_apertura_anticipada_sin_fecha_es_rechazada():
    try:
        IncidenciaDTO(
            descripcion="Necesito abrir el lab antes de hora",
            tipo_falla=TipoFallaEnum.HARDWARE,
            id_laboratorio=1,
            tipo_requerimiento=TipoRequerimientoEnum.APERTURA_ANTICIPADA,
            fecha_hora_apertura=None,
        )
    except ValidacionException as exc:
        assert exc.campo == "fecha_hora_apertura"
        return
    raise AssertionError("Se esperaba ValidacionException por fecha_hora_apertura faltante")


def test_resolver_sin_nota_publica_es_rechazado():
    entorno = _construir_entorno()
    svc = entorno["incidencia_service"]

    datos = IncidenciaDTO(descripcion="El proyector no enciende", tipo_falla=TipoFallaEnum.HARDWARE, id_laboratorio=1)
    incidencia = svc.registrar_incidencia(entorno["docente"], datos)
    svc.asignar_tecnico(entorno["administrador"], incidencia.id_incidencia, entorno["tecnico"], PrioridadEnum.MEDIA)
    svc.cambiar_estado(entorno["tecnico"], incidencia.id_incidencia, EstadoIncidenciaEnum.EN_PROCESO)

    try:
        svc.cambiar_estado(entorno["tecnico"], incidencia.id_incidencia, EstadoIncidenciaEnum.RESUELTO)
    except ValidacionException as exc:
        assert exc.campo == "estado"
        return
    raise AssertionError("Se esperaba ValidacionException por falta de nota publica")


def test_resolver_con_nota_publica_funciona():
    entorno = _construir_entorno()
    svc = entorno["incidencia_service"]
    notas_svc = entorno["nota_tecnica_service"]

    datos = IncidenciaDTO(descripcion="Sin internet", tipo_falla=TipoFallaEnum.RED, id_laboratorio=1)
    incidencia = svc.registrar_incidencia(entorno["docente"], datos)
    svc.asignar_tecnico(entorno["administrador"], incidencia.id_incidencia, entorno["tecnico"], PrioridadEnum.ALTA)
    svc.cambiar_estado(entorno["tecnico"], incidencia.id_incidencia, EstadoIncidenciaEnum.EN_PROCESO)

    from app.dtos.nota_tecnica_dto import NotaTecnicaDTO

    notas_svc.agregar_nota(entorno["tecnico"], incidencia.id_incidencia, NotaTecnicaDTO("Se reinicio el router", False))
    resultado = svc.cambiar_estado(entorno["tecnico"], incidencia.id_incidencia, EstadoIncidenciaEnum.RESUELTO)
    assert resultado.estado == EstadoIncidenciaEnum.RESUELTO


def test_calificar_ticket_no_resuelto_es_rechazado():
    entorno = _construir_entorno()
    svc = entorno["incidencia_service"]

    datos = IncidenciaDTO(descripcion="PC lenta", tipo_falla=TipoFallaEnum.HARDWARE, id_laboratorio=1)
    incidencia = svc.registrar_incidencia(entorno["docente"], datos)
    svc.asignar_tecnico(entorno["administrador"], incidencia.id_incidencia, entorno["tecnico"], PrioridadEnum.BAJA)

    try:
        entorno["calificacion_service"].calificar(entorno["docente"], incidencia.id_incidencia, 5, None)
    except ValidacionException as exc:
        assert exc.campo == "estado"
        return
    raise AssertionError("Se esperaba ValidacionException por calificar un ticket no resuelto")


def test_calificar_ticket_ajeno_es_rechazado():
    entorno = _construir_entorno()
    svc = entorno["incidencia_service"]
    notas_svc = entorno["nota_tecnica_service"]

    datos = IncidenciaDTO(descripcion="Mouse no funciona", tipo_falla=TipoFallaEnum.HARDWARE, id_laboratorio=1)
    incidencia = svc.registrar_incidencia(entorno["docente"], datos)
    svc.asignar_tecnico(entorno["administrador"], incidencia.id_incidencia, entorno["tecnico"], PrioridadEnum.MEDIA)
    svc.cambiar_estado(entorno["tecnico"], incidencia.id_incidencia, EstadoIncidenciaEnum.EN_PROCESO)

    from app.dtos.nota_tecnica_dto import NotaTecnicaDTO

    notas_svc.agregar_nota(entorno["tecnico"], incidencia.id_incidencia, NotaTecnicaDTO("Se cambio el mouse", False))
    svc.cambiar_estado(entorno["tecnico"], incidencia.id_incidencia, EstadoIncidenciaEnum.RESUELTO)

    try:
        entorno["calificacion_service"].calificar(entorno["otro_docente"], incidencia.id_incidencia, 3, None)
    except AccesoDenegadoException:
        return
    raise AssertionError("Se esperaba AccesoDenegadoException: el docente no es el dueno del ticket")


def test_calificar_dos_veces_es_rechazado():
    entorno = _construir_entorno()
    svc = entorno["incidencia_service"]
    notas_svc = entorno["nota_tecnica_service"]

    datos = IncidenciaDTO(descripcion="Teclado no responde", tipo_falla=TipoFallaEnum.HARDWARE, id_laboratorio=1)
    incidencia = svc.registrar_incidencia(entorno["docente"], datos)
    svc.asignar_tecnico(entorno["administrador"], incidencia.id_incidencia, entorno["tecnico"], PrioridadEnum.MEDIA)
    svc.cambiar_estado(entorno["tecnico"], incidencia.id_incidencia, EstadoIncidenciaEnum.EN_PROCESO)

    from app.dtos.nota_tecnica_dto import NotaTecnicaDTO

    notas_svc.agregar_nota(entorno["tecnico"], incidencia.id_incidencia, NotaTecnicaDTO("Se cambio el teclado", False))
    svc.cambiar_estado(entorno["tecnico"], incidencia.id_incidencia, EstadoIncidenciaEnum.RESUELTO)

    entorno["calificacion_service"].calificar(entorno["docente"], incidencia.id_incidencia, 4, "Bien")
    try:
        entorno["calificacion_service"].calificar(entorno["docente"], incidencia.id_incidencia, 2, "otra vez")
    except ValidacionException as exc:
        assert exc.campo == "id_incidencia"
        return
    raise AssertionError("Se esperaba ValidacionException: el ticket ya fue calificado")


def test_docente_no_ve_notas_privadas():
    entorno = _construir_entorno()
    svc = entorno["incidencia_service"]
    notas_svc = entorno["nota_tecnica_service"]

    datos = IncidenciaDTO(descripcion="Falla electrica", tipo_falla=TipoFallaEnum.ELECTRICIDAD, id_laboratorio=1)
    incidencia = svc.registrar_incidencia(entorno["docente"], datos)
    svc.asignar_tecnico(entorno["administrador"], incidencia.id_incidencia, entorno["tecnico"], PrioridadEnum.MEDIA)

    from app.dtos.nota_tecnica_dto import NotaTecnicaDTO

    notas_svc.agregar_nota(entorno["tecnico"], incidencia.id_incidencia, NotaTecnicaDTO("Diagnostico interno: fusible quemado", True))
    notas_svc.agregar_nota(entorno["tecnico"], incidencia.id_incidencia, NotaTecnicaDTO("Se cambio el fusible", False))

    notas_para_docente = notas_svc.listar_visibles_para(entorno["docente"], incidencia.id_incidencia)
    assert len(notas_para_docente) == 1
    assert notas_para_docente[0].es_privado is False

    notas_para_tecnico = notas_svc.listar_visibles_para(entorno["tecnico"], incidencia.id_incidencia)
    assert len(notas_para_tecnico) == 2


def test_tecnico_no_puede_operar_ticket_ajeno():
    entorno = _construir_entorno()
    svc = entorno["incidencia_service"]
    otro_tecnico = Tecnico(5, "T002", "Carlos", "Diaz", "carlos@ucv.edu.pe", "hash", especialidad="Hardware")

    datos = IncidenciaDTO(descripcion="Sin señal de video", tipo_falla=TipoFallaEnum.HARDWARE, id_laboratorio=1)
    incidencia = svc.registrar_incidencia(entorno["docente"], datos)
    svc.asignar_tecnico(entorno["administrador"], incidencia.id_incidencia, entorno["tecnico"], PrioridadEnum.MEDIA)

    try:
        svc.cambiar_estado(otro_tecnico, incidencia.id_incidencia, EstadoIncidenciaEnum.EN_PROCESO)
    except AccesoDenegadoException:
        return
    raise AssertionError("Se esperaba AccesoDenegadoException: el ticket no esta asignado a otro_tecnico")


def test_laboratorio_en_mantenimiento_rechaza_tickets_nuevos():
    entorno = _construir_entorno()
    svc = entorno["incidencia_service"]
    laboratorio = entorno["incidencia_service"]._laboratorios.obtener_por_id(1)
    laboratorio.actualizar_estado_operativo(False)

    datos = IncidenciaDTO(descripcion="Otro problema", tipo_falla=TipoFallaEnum.HARDWARE, id_laboratorio=1)
    try:
        svc.registrar_incidencia(entorno["docente"], datos)
    except ValidacionException as exc:
        assert exc.campo == "id_laboratorio"
        return
    raise AssertionError("Se esperaba ValidacionException: laboratorio en mantenimiento")


def test_apertura_anticipada_sin_tipo_falla_funciona():
    """Una solicitud de apertura anticipada no es una falla tecnica: no debe exigir tipo_falla."""
    entorno = _construir_entorno()
    svc = entorno["incidencia_service"]
    from datetime import datetime, timedelta

    datos = IncidenciaDTO(
        descripcion="Necesito el lab abierto antes de mi clase",
        id_laboratorio=1,
        tipo_requerimiento=TipoRequerimientoEnum.APERTURA_ANTICIPADA,
        fecha_hora_apertura=datetime.now() + timedelta(hours=2),
    )
    incidencia = svc.registrar_incidencia(entorno["docente"], datos)
    assert incidencia.tipo_falla is None


def test_falla_tecnica_sin_tipo_falla_es_rechazada():
    try:
        IncidenciaDTO(descripcion="Algo esta fallando", id_laboratorio=1)
    except ValidacionException as exc:
        assert exc.campo == "tipo_falla"
        return
    raise AssertionError("Se esperaba ValidacionException: una falla tecnica requiere tipo_falla")


TESTS = [
    test_apertura_anticipada_sin_fecha_es_rechazada,
    test_apertura_anticipada_sin_tipo_falla_funciona,
    test_falla_tecnica_sin_tipo_falla_es_rechazada,
    test_resolver_sin_nota_publica_es_rechazado,
    test_resolver_con_nota_publica_funciona,
    test_calificar_ticket_no_resuelto_es_rechazado,
    test_calificar_ticket_ajeno_es_rechazado,
    test_calificar_dos_veces_es_rechazado,
    test_docente_no_ve_notas_privadas,
    test_tecnico_no_puede_operar_ticket_ajeno,
    test_laboratorio_en_mantenimiento_rechaza_tickets_nuevos,
]


def main() -> int:
    fallos = 0
    for test in TESTS:
        nombre = test.__name__
        try:
            test()
            print(f"PASO  {nombre}")
        except Exception as exc:  # noqa: BLE001 - queremos reportar cualquier falla, no relanzar
            fallos += 1
            print(f"FALLO {nombre}: {exc}")
    total = len(TESTS)
    print(f"\n{total - fallos}/{total} pruebas pasaron")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
