from app.controllers.auth_controller import crear_router_auth
from app.controllers.chatbot_controller import crear_router_chatbot
from app.controllers.dashboard_controller import crear_router_dashboard
from app.controllers.equipo_controller import crear_router_equipos
from app.controllers.evidencia_controller import crear_router_evidencias
from app.controllers.incidencia_controller import crear_router_incidencias
from app.controllers.laboratorio_controller import crear_router_laboratorios
from app.controllers.nota_tecnica_controller import crear_router_notas_tecnicas
from app.controllers.notificacion_controller import crear_router_notificaciones
from app.controllers.reporte_controller import crear_router_reportes
from app.controllers.usuario_controller import crear_router_usuarios

__all__ = [
    "crear_router_auth",
    "crear_router_chatbot",
    "crear_router_dashboard",
    "crear_router_equipos",
    "crear_router_evidencias",
    "crear_router_incidencias",
    "crear_router_laboratorios",
    "crear_router_notas_tecnicas",
    "crear_router_notificaciones",
    "crear_router_reportes",
    "crear_router_usuarios",
]
