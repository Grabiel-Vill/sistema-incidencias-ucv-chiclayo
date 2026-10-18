import os
from pathlib import Path

_RUTA_ENV_POR_DEFECTO = Path(__file__).resolve().parents[2] / ".env"


class Settings:
    """Carga variables de entorno (.env) y expone acceso tipado a parametros globales."""

    def __init__(self, ruta_env: Path | str | None = None):
        self._valores: dict[str, str] = dict(os.environ)
        ruta = Path(ruta_env) if ruta_env else _RUTA_ENV_POR_DEFECTO
        if ruta.exists():
            self._valores.update(self._parsear_env(ruta))

    @staticmethod
    def _parsear_env(ruta: Path) -> dict[str, str]:
        valores: dict[str, str] = {}
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, _, valor = linea.partition("=")
            valores[clave.strip()] = valor.strip().strip('"').strip("'")
        return valores

    def obtener(self, clave: str, por_defecto: str | None = None) -> str | None:
        return self._valores.get(clave, por_defecto)

    def obtener_entero(self, clave: str, por_defecto: int) -> int:
        valor = self._valores.get(clave)
        return int(valor) if valor is not None and valor.strip() != "" else por_defecto

    def obtener_booleano(self, clave: str, por_defecto: bool = False) -> bool:
        valor = self._valores.get(clave)
        if valor is None or valor.strip() == "":
            return por_defecto
        return valor.strip().lower() in {"1", "true", "yes", "on"}

    def obtener_lista(self, clave: str, separador: str = ",") -> list[str]:
        valor = self._valores.get(clave)
        if not valor:
            return []
        return [item.strip() for item in valor.split(separador) if item.strip()]

    @property
    def entorno(self) -> str:
        return self.obtener("APP_ENV", "development")

    @property
    def es_produccion(self) -> bool:
        return self.entorno.lower() == "production"
