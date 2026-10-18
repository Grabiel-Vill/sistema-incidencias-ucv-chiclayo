from app.models.evidencia import Evidencia
from app.models.incidencia import Incidencia
from app.repositories.evidencia_repository import EvidenciaRepository
from app.utils.file_storage import FileStorage


class EvidenciaService:
    """Valida y almacena imagenes de evidencia asociadas a una Incidencia (RF1)."""

    def __init__(self, evidencia_repository: EvidenciaRepository, file_storage: FileStorage | None = None):
        self._evidencias = evidencia_repository
        self._file_storage = file_storage or FileStorage()

    def agregar_evidencia(self, incidencia: Incidencia, nombre_archivo: str, contenido: bytes) -> Evidencia:
        url_relativa = self._file_storage.guardar_imagen(nombre_archivo, contenido)
        evidencia = Evidencia(id_evidencia=self._evidencias.siguiente_id(), url_imagen=url_relativa)
        incidencia.agregar_evidencia(evidencia)
        self._evidencias.agregar(evidencia)
        return evidencia
