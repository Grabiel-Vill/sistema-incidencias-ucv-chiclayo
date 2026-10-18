"""Pruebas de integracion contra el backend REAL corriendo sobre SQL Server (no en memoria).

Requiere el backend arriba en http://localhost:8000 (python -m uvicorn app.main:app) y la
base de datos sistema_incidencias_ucv accesible (ver backend/.env). No usa pytest ni
dependencias nuevas: solo urllib de la libreria estandar. Cada prueba crea sus propios datos
(usuarios/laboratorio/tickets) para no depender ni ensuciar el estado de otras corridas.

Correr con: python tests/integration/test_reglas_negocio_sql_server.py
"""

from __future__ import annotations

import json
import secrets
import urllib.error
import urllib.request

BASE = "http://localhost:8000"


class ApiError(Exception):
    def __init__(self, status: int, body: dict):
        self.status = status
        self.body = body
        super().__init__(f"HTTP {status}: {body}")


def llamar(metodo: str, ruta: str, token: str | None = None, cuerpo: dict | None = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(BASE + ruta, data=data, headers=headers, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            texto = resp.read().decode()
            return resp.status, (json.loads(texto) if texto else None)
    except urllib.error.HTTPError as exc:
        texto = exc.read().decode()
        cuerpo_error = json.loads(texto) if texto else {}
        raise ApiError(exc.code, cuerpo_error) from None


def login(email: str, password: str) -> str:
    _, resp = llamar("POST", "/auth/login", cuerpo={"email": email, "password": password})
    return resp["access_token"]


class Entorno:
    """Crea un docente, un técnico y un laboratorio nuevos (via API) para cada prueba,
    usando el token de admin ya sembrado (admin@ucv.edu.pe/Admin123, ver 02_seed.sql)."""

    def __init__(self):
        self.admin_token = login("admin@ucv.edu.pe", "Admin123")
        sufijo = secrets.token_hex(3)

        _, lab = llamar(
            "POST", "/laboratorios", token=self.admin_token,
            cuerpo={"nombre": f"Lab Pruebas {sufijo}", "pabellon": "Z", "piso": 9},
        )
        self.id_laboratorio = lab["id_laboratorio"]

        _, docente = llamar(
            "POST", "/usuarios", token=self.admin_token,
            cuerpo={
                "codigo_ucv": f"PD{sufijo}", "nombre": "Prueba", "apellido": f"Docente{sufijo}",
                "email": f"prueba.docente.{sufijo}@ucv.edu.pe", "password": "Prueba123", "rol": "DOCENTE",
            },
        )
        self.docente_token = login(docente["email"], "Prueba123")
        self.id_docente = docente["id_usuario"]

        _, otro_docente = llamar(
            "POST", "/usuarios", token=self.admin_token,
            cuerpo={
                "codigo_ucv": f"PD2{sufijo}", "nombre": "Prueba", "apellido": f"Docente2{sufijo}",
                "email": f"prueba.docente2.{sufijo}@ucv.edu.pe", "password": "Prueba123", "rol": "DOCENTE",
            },
        )
        self.otro_docente_token = login(otro_docente["email"], "Prueba123")

        _, tecnico = llamar(
            "POST", "/usuarios", token=self.admin_token,
            cuerpo={
                "codigo_ucv": f"PT{sufijo}", "nombre": "Prueba", "apellido": f"Tecnico{sufijo}",
                "email": f"prueba.tecnico.{sufijo}@ucv.edu.pe", "password": "Prueba123", "rol": "TECNICO",
                "especialidad": "General",
            },
        )
        self.tecnico_token = login(tecnico["email"], "Prueba123")
        self.id_tecnico = tecnico["id_usuario"]

        _, otro_tecnico = llamar(
            "POST", "/usuarios", token=self.admin_token,
            cuerpo={
                "codigo_ucv": f"PT2{sufijo}", "nombre": "Prueba", "apellido": f"Tecnico2{sufijo}",
                "email": f"prueba.tecnico2.{sufijo}@ucv.edu.pe", "password": "Prueba123", "rol": "TECNICO",
                "especialidad": "General",
            },
        )
        self.otro_tecnico_token = login(otro_tecnico["email"], "Prueba123")

    def crear_ticket(self, descripcion="Falla de prueba", tipo_falla="HARDWARE"):
        _, inc = llamar(
            "POST", "/incidencias", token=self.docente_token,
            cuerpo={"descripcion": descripcion, "tipo_falla": tipo_falla, "id_laboratorio": self.id_laboratorio},
        )
        return inc

    def asignar_y_poner_en_proceso(self, id_incidencia: int, token_tecnico: str | None = None, id_tecnico: int | None = None):
        token_tecnico = token_tecnico or self.tecnico_token
        id_tecnico = id_tecnico or self.id_tecnico
        llamar(
            "POST", f"/incidencias/{id_incidencia}/asignar", token=self.admin_token,
            cuerpo={"id_tecnico": id_tecnico, "prioridad": "MEDIA"},
        )
        llamar("PATCH", f"/incidencias/{id_incidencia}/estado", token=token_tecnico, cuerpo={"estado": "EN_PROCESO"})


def test_apertura_anticipada_sin_fecha_es_rechazada():
    entorno = Entorno()
    try:
        llamar(
            "POST", "/incidencias", token=entorno.docente_token,
            cuerpo={
                "descripcion": "Apertura sin fecha", "tipo_falla": "HARDWARE",
                "id_laboratorio": entorno.id_laboratorio, "tipo_requerimiento": "APERTURA_ANTICIPADA",
            },
        )
    except ApiError as exc:
        assert exc.status == 422
        return
    raise AssertionError("Se esperaba 422 por fecha_hora_apertura faltante")


def test_apertura_anticipada_con_fecha_pasada_es_rechazada():
    entorno = Entorno()
    try:
        llamar(
            "POST", "/incidencias", token=entorno.docente_token,
            cuerpo={
                "descripcion": "Apertura con fecha pasada", "tipo_falla": "HARDWARE",
                "id_laboratorio": entorno.id_laboratorio, "tipo_requerimiento": "APERTURA_ANTICIPADA",
                "fecha_hora_apertura": "2020-01-01T08:00:00",
            },
        )
    except ApiError as exc:
        assert exc.status == 422
        return
    raise AssertionError("Se esperaba 422 por fecha_hora_apertura en el pasado")


def test_resolver_sin_nota_publica_es_rechazado():
    entorno = Entorno()
    ticket = entorno.crear_ticket()
    entorno.asignar_y_poner_en_proceso(ticket["id_incidencia"])
    try:
        llamar(
            "PATCH", f"/incidencias/{ticket['id_incidencia']}/estado", token=entorno.tecnico_token,
            cuerpo={"estado": "RESUELTO"},
        )
    except ApiError as exc:
        assert exc.status == 422
        return
    raise AssertionError("Se esperaba 422 por falta de nota publica")


def test_resolver_con_nota_publica_funciona():
    entorno = Entorno()
    ticket = entorno.crear_ticket()
    entorno.asignar_y_poner_en_proceso(ticket["id_incidencia"])
    llamar(
        "POST", f"/incidencias/{ticket['id_incidencia']}/notas", token=entorno.tecnico_token,
        cuerpo={"contenido": "Se soluciono reemplazando el cable", "es_privado": False},
    )
    _, resuelto = llamar(
        "PATCH", f"/incidencias/{ticket['id_incidencia']}/estado", token=entorno.tecnico_token,
        cuerpo={"estado": "RESUELTO"},
    )
    assert resuelto["estado"] == "RESUELTO"


def test_calificar_ticket_no_resuelto_es_rechazado():
    entorno = Entorno()
    ticket = entorno.crear_ticket()
    entorno.asignar_y_poner_en_proceso(ticket["id_incidencia"])
    try:
        llamar(
            "POST", f"/incidencias/{ticket['id_incidencia']}/calificacion", token=entorno.docente_token,
            cuerpo={"estrellas": 5, "comentario": None},
        )
    except ApiError as exc:
        assert exc.status == 422
        return
    raise AssertionError("Se esperaba 422: ticket no esta resuelto")


def test_calificar_ticket_ajeno_es_rechazado():
    entorno = Entorno()
    ticket = entorno.crear_ticket()
    entorno.asignar_y_poner_en_proceso(ticket["id_incidencia"])
    llamar(
        "POST", f"/incidencias/{ticket['id_incidencia']}/notas", token=entorno.tecnico_token,
        cuerpo={"contenido": "Resuelto", "es_privado": False},
    )
    llamar("PATCH", f"/incidencias/{ticket['id_incidencia']}/estado", token=entorno.tecnico_token, cuerpo={"estado": "RESUELTO"})
    try:
        llamar(
            "POST", f"/incidencias/{ticket['id_incidencia']}/calificacion", token=entorno.otro_docente_token,
            cuerpo={"estrellas": 3, "comentario": None},
        )
    except ApiError as exc:
        assert exc.status == 403
        return
    raise AssertionError("Se esperaba 403: el docente no es el dueno del ticket")


def test_calificar_dos_veces_es_rechazado():
    entorno = Entorno()
    ticket = entorno.crear_ticket()
    entorno.asignar_y_poner_en_proceso(ticket["id_incidencia"])
    llamar(
        "POST", f"/incidencias/{ticket['id_incidencia']}/notas", token=entorno.tecnico_token,
        cuerpo={"contenido": "Resuelto", "es_privado": False},
    )
    llamar("PATCH", f"/incidencias/{ticket['id_incidencia']}/estado", token=entorno.tecnico_token, cuerpo={"estado": "RESUELTO"})
    llamar(
        "POST", f"/incidencias/{ticket['id_incidencia']}/calificacion", token=entorno.docente_token,
        cuerpo={"estrellas": 4, "comentario": "Bien"},
    )
    try:
        llamar(
            "POST", f"/incidencias/{ticket['id_incidencia']}/calificacion", token=entorno.docente_token,
            cuerpo={"estrellas": 2, "comentario": "otra vez"},
        )
    except ApiError as exc:
        assert exc.status == 422
        return
    raise AssertionError("Se esperaba 422: el ticket ya fue calificado")


def test_docente_no_ve_notas_privadas():
    entorno = Entorno()
    ticket = entorno.crear_ticket()
    entorno.asignar_y_poner_en_proceso(ticket["id_incidencia"])
    llamar(
        "POST", f"/incidencias/{ticket['id_incidencia']}/notas", token=entorno.tecnico_token,
        cuerpo={"contenido": "Diagnostico interno", "es_privado": True},
    )
    llamar(
        "POST", f"/incidencias/{ticket['id_incidencia']}/notas", token=entorno.tecnico_token,
        cuerpo={"contenido": "Nota publica de solucion", "es_privado": False},
    )
    _, notas_docente = llamar("GET", f"/incidencias/{ticket['id_incidencia']}/notas", token=entorno.docente_token)
    assert len(notas_docente) == 1 and notas_docente[0]["es_privado"] is False

    _, notas_tecnico = llamar("GET", f"/incidencias/{ticket['id_incidencia']}/notas", token=entorno.tecnico_token)
    assert len(notas_tecnico) == 2


def test_tecnico_no_puede_operar_ticket_ajeno():
    entorno = Entorno()
    ticket = entorno.crear_ticket()
    entorno.asignar_y_poner_en_proceso(ticket["id_incidencia"])
    try:
        llamar(
            "PATCH", f"/incidencias/{ticket['id_incidencia']}/estado", token=entorno.otro_tecnico_token,
            cuerpo={"estado": "RESUELTO"},
        )
    except ApiError as exc:
        assert exc.status == 403
        return
    raise AssertionError("Se esperaba 403: el ticket no esta asignado a otro_tecnico")


def test_tecnico_no_ve_tickets_ajenos_en_su_bandeja():
    entorno = Entorno()
    ticket = entorno.crear_ticket()
    entorno.asignar_y_poner_en_proceso(ticket["id_incidencia"])
    _, bandeja_ajena = llamar(
        "GET", f"/incidencias?id_tecnico={entorno.id_tecnico}", token=entorno.otro_tecnico_token,
    )
    ids = [i["id_incidencia"] for i in bandeja_ajena]
    assert ticket["id_incidencia"] not in ids, "El backend no deberia dejar ver tickets de otro tecnico"


def test_laboratorio_en_mantenimiento_rechaza_tickets_nuevos():
    entorno = Entorno()
    llamar(
        "PUT", f"/laboratorios/{entorno.id_laboratorio}", token=entorno.admin_token,
        cuerpo={"nombre": "Lab Pruebas", "pabellon": "Z", "piso": 9, "estado_operativo": False},
    )
    try:
        entorno.crear_ticket(descripcion="No deberia poder crearse")
    except ApiError as exc:
        assert exc.status == 422
        return
    raise AssertionError("Se esperaba 422: laboratorio en mantenimiento")


TESTS = [
    test_apertura_anticipada_sin_fecha_es_rechazada,
    test_apertura_anticipada_con_fecha_pasada_es_rechazada,
    test_resolver_sin_nota_publica_es_rechazado,
    test_resolver_con_nota_publica_funciona,
    test_calificar_ticket_no_resuelto_es_rechazado,
    test_calificar_ticket_ajeno_es_rechazado,
    test_calificar_dos_veces_es_rechazado,
    test_docente_no_ve_notas_privadas,
    test_tecnico_no_puede_operar_ticket_ajeno,
    test_tecnico_no_ve_tickets_ajenos_en_su_bandeja,
    test_laboratorio_en_mantenimiento_rechaza_tickets_nuevos,
]


def main() -> int:
    try:
        urllib.request.urlopen(BASE + "/docs", timeout=5)
    except Exception as exc:  # noqa: BLE001
        print(f"No se pudo contactar al backend en {BASE}: {exc}")
        return 2

    fallos = 0
    for test in TESTS:
        nombre = test.__name__
        try:
            test()
            print(f"PASO  {nombre}")
        except Exception as exc:  # noqa: BLE001
            fallos += 1
            print(f"FALLO {nombre}: {exc}")
    total = len(TESTS)
    print(f"\n{total - fallos}/{total} pruebas pasaron (contra SQL Server real en {BASE})")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
