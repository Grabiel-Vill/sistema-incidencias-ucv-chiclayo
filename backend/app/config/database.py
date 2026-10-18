from app.config.settings import Settings


class DatabaseConnection:
    """Conexion a SQL Server (RNF1) via pyodbc.

    Los repositorios consultan `esta_configurado` para decidir si operan contra SQL Server
    o si usan su almacen en memoria como respaldo (mismo patron de degradacion que
    EmailClient/LLMClient): el backend sigue siendo arrancable y testeable sin una instancia
    real de SQL Server, y se activa solo en cuanto DB_USER/DB_PASSWORD/DB_NAME existen en .env.
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()
        self.host = self._settings.obtener("DB_HOST", "localhost")
        self.puerto = self._settings.obtener_entero("DB_PORT", 1433)
        self.usuario = self._settings.obtener("DB_USER")
        self.password = self._settings.obtener("DB_PASSWORD")
        self.nombre_bd = self._settings.obtener("DB_NAME")
        self.driver = self._settings.obtener("DB_DRIVER", "ODBC Driver 17 for SQL Server")

    @property
    def esta_configurado(self) -> bool:
        return all([self.usuario, self.password, self.nombre_bd])

    @property
    def cadena_conexion(self) -> str:
        return f"mssql://{self.usuario}:***@{self.host}:{self.puerto}/{self.nombre_bd}"

    def conectar(self):
        if not self.esta_configurado:
            raise RuntimeError(
                "DB_USER, DB_PASSWORD y DB_NAME deben estar definidos en .env antes de conectar a SQL Server"
            )
        try:
            import pyodbc
        except ImportError as exc:
            raise RuntimeError(
                "Falta el driver 'pyodbc'. Instalalo con 'pip install pyodbc' (requiere tener instalado "
                "el ODBC Driver 17 o 18 for SQL Server del sistema operativo, eso no lo instala pip)."
            ) from exc

        # Instancia nombrada (host\instancia, ej. "localhost\HERRERA"): no se antepone el
        # puerto porque la resolucion la hace el propio driver (named pipes/shared memory
        # localmente), a diferencia de una instancia default identificada solo por host:puerto.
        servidor = self.host if "\\" in self.host else f"{self.host},{self.puerto}"
        cadena = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={servidor};"
            f"DATABASE={self.nombre_bd};"
            f"UID={self.usuario};"
            f"PWD={self.password};"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(cadena, autocommit=False)
