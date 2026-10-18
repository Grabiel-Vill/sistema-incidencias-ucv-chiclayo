# Sistema de Incidencias UCV Chiclayo

Sistema web para reportar y gestionar incidencias de laboratorios de computo (fallas tecnicas
y solicitudes de apertura anticipada), con roles de Docente, Tecnico y Administrador.

- **Backend:** Python + FastAPI, capas Controller -> Service -> Repository -> Model, SQL Server.
- **Frontend:** HTML/CSS/JS vanilla (sin frameworks), modulos ES.

Ver [CHANGELOG.md](CHANGELOG.md) para el detalle de funcionalidades por fase y
[docs/ARQUITECTURA.md](docs/ARQUITECTURA.md) para el diseño de capas.

## Requisitos

- Python 3.11+
- SQL Server (local o remoto) con ODBC Driver 17 instalado
- Un servidor estatico simple para el frontend (por ejemplo `npx serve` o la extension
  Live Server de VS Code)

## Configuracion

1. Instala las dependencias del backend:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Crea la base de datos ejecutando en orden los scripts de `backend/database/`
   (`01_schema.sql`, `02_...`, etc.) contra tu instancia de SQL Server.

3. Copia `backend/.env.example` a `backend/.env` y completa tus propios valores
   (usuario, contraseña y host de tu SQL Server, y un `JWT_SECRET` propio).

## Ejecutar en desarrollo

```bash
# Backend (desde backend/)
python -m uvicorn app.main:app --reload --port 8000

# Frontend (desde backend/app/vistas/)
npx serve -l 5500
```

Luego abre `http://localhost:5500/pages/login.html`.
