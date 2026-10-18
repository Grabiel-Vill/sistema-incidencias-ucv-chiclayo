from app.repositories.base_repository import BaseRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.equipo_repository import EquipoRepository
from app.repositories.evidencia_repository import EvidenciaRepository
from app.repositories.incidencia_repository import IncidenciaRepository
from app.repositories.laboratorio_repository import LaboratorioRepository
from app.repositories.nota_tecnica_repository import NotaTecnicaRepository
from app.repositories.notificacion_repository import NotificacionRepository
from app.repositories.reporte_repository import ReporteRepository
from app.repositories.usuario_repository import UsuarioRepository

__all__ = [
    "BaseRepository",
    "CalificacionRepository",
    "EquipoRepository",
    "EvidenciaRepository",
    "IncidenciaRepository",
    "LaboratorioRepository",
    "NotaTecnicaRepository",
    "NotificacionRepository",
    "ReporteRepository",
    "UsuarioRepository",
]
