from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import DatabaseConnection, LLMConfig, SecurityConfig, Settings
from app.controllers import (
    crear_router_auth,
    crear_router_chatbot,
    crear_router_dashboard,
    crear_router_equipos,
    crear_router_evidencias,
    crear_router_incidencias,
    crear_router_laboratorios,
    crear_router_notas_tecnicas,
    crear_router_notificaciones,
    crear_router_reportes,
    crear_router_usuarios,
)
from app.integrations import EmailClient, LLMClient
from app.middleware import crear_dependencia_rol, crear_dependencia_usuario_actual, registrar_manejadores_de_error
from app.models.enums import RolEnum
from app.repositories import (
    CalificacionRepository,
    EquipoRepository,
    EvidenciaRepository,
    IncidenciaRepository,
    LaboratorioRepository,
    NotaTecnicaRepository,
    NotificacionRepository,
    ReporteRepository,
    UsuarioRepository,
)
from app.services import (
    AsistenteIAService,
    AuthService,
    CalificacionService,
    ChatbotService,
    DashboardService,
    EquipoService,
    EvidenciaService,
    IncidenciaService,
    LaboratorioService,
    NotaTecnicaService,
    NotificacionService,
    ReporteService,
    UsuarioService,
)


def crear_app() -> FastAPI:
    """Composition root: arma repositorios, servicios, middleware y controllers (MVC + capas)."""

    settings = Settings()
    security_config = SecurityConfig(settings)
    llm_config = LLMConfig(settings)
    database = DatabaseConnection(settings)

    usuario_repo = UsuarioRepository(database)
    laboratorio_repo = LaboratorioRepository(database)
    equipo_repo = EquipoRepository(database)
    incidencia_repo = IncidenciaRepository(database, laboratorio_repo, usuario_repo)
    evidencia_repo = EvidenciaRepository(database)
    nota_tecnica_repo = NotaTecnicaRepository(database)
    notificacion_repo = NotificacionRepository(database)
    reporte_repo = ReporteRepository(database)
    calificacion_repo = CalificacionRepository(database)

    email_client = EmailClient(settings)
    llm_client = LLMClient(llm_config) if llm_config.esta_configurado else None

    auth_service = AuthService(usuario_repo, security_config)
    usuario_service = UsuarioService(usuario_repo)
    laboratorio_service = LaboratorioService(laboratorio_repo, incidencia_repo)
    equipo_service = EquipoService(equipo_repo, laboratorio_repo)
    notificacion_service = NotificacionService(notificacion_repo, email_client)
    incidencia_service = IncidenciaService(
        incidencia_repo, laboratorio_repo, equipo_repo, notificacion_service, nota_tecnica_repo, calificacion_repo
    )
    nota_tecnica_service = NotaTecnicaService(nota_tecnica_repo, incidencia_repo)
    evidencia_service = EvidenciaService(evidencia_repo)
    calificacion_service = CalificacionService(calificacion_repo, incidencia_repo)
    asistente_ia_service = AsistenteIAService(llm_client)
    chatbot_service = ChatbotService(asistente_ia_service)
    reporte_service = ReporteService(reporte_repo, incidencia_repo)
    dashboard_service = DashboardService(reporte_service, calificacion_repo)

    obtener_usuario_actual = crear_dependencia_usuario_actual(auth_service)
    requiere_docente = crear_dependencia_rol(obtener_usuario_actual, RolEnum.DOCENTE)
    requiere_tecnico = crear_dependencia_rol(obtener_usuario_actual, RolEnum.TECNICO)
    requiere_administrador = crear_dependencia_rol(obtener_usuario_actual, RolEnum.ADMINISTRADOR)
    requiere_tecnico_o_administrador = crear_dependencia_rol(
        obtener_usuario_actual, RolEnum.TECNICO, RolEnum.ADMINISTRADOR
    )

    app = FastAPI(title="Sistema de Incidencias UCV Chiclayo", version="0.1.0")
    registrar_manejadores_de_error(app)

    # El frontend (HTML/JS/CSS plano) se sirve desde un origen distinto al backend
    # (file:// o un servidor estatico), por lo que el navegador exige CORS habilitado.
    # Sin credenciales/cookies (la sesion viaja en el header Authorization), "*" es seguro.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=security_config.cors_origenes_permitidos or ["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Sirve storage/evidencias para que el frontend muestre las fotos subidas por el docente
    # (evidencia_service.guardar_imagen devuelve rutas relativas tipo "evidencias/<uuid>.jpg").
    directorio_storage = Path(__file__).resolve().parent.parent / "storage"
    app.mount("/storage", StaticFiles(directory=str(directorio_storage)), name="storage")

    # Expuestos en app.state para scripts de arranque/seed y para pruebas (ver tests/).
    app.state.usuario_repository = usuario_repo
    app.state.laboratorio_repository = laboratorio_repo
    app.state.equipo_repository = equipo_repo
    app.state.security_config = security_config

    app.include_router(crear_router_auth(auth_service, obtener_usuario_actual))
    app.include_router(crear_router_usuarios(usuario_service, requiere_administrador))
    app.include_router(crear_router_laboratorios(laboratorio_service, requiere_administrador))
    app.include_router(crear_router_equipos(equipo_service, requiere_administrador, requiere_tecnico_o_administrador))
    app.include_router(
        crear_router_incidencias(
            incidencia_service,
            calificacion_service,
            usuario_repo,
            obtener_usuario_actual,
            requiere_docente,
            requiere_tecnico,
            requiere_administrador,
            requiere_tecnico_o_administrador,
        )
    )
    app.include_router(crear_router_notas_tecnicas(nota_tecnica_service, obtener_usuario_actual, requiere_tecnico))
    app.include_router(crear_router_evidencias(evidencia_service, incidencia_repo, obtener_usuario_actual))
    app.include_router(crear_router_chatbot(chatbot_service, requiere_docente))
    app.include_router(crear_router_notificaciones(notificacion_repo, obtener_usuario_actual))
    app.include_router(crear_router_dashboard(dashboard_service, requiere_administrador))
    app.include_router(crear_router_reportes(reporte_service, reporte_repo, requiere_administrador))

    return app


app = crear_app()
