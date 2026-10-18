import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    AccesoDenegadoException,
    AppException,
    CredencialesInvalidasException,
    RecursoNoEncontradoException,
    TransicionEstadoInvalidaException,
    ValidacionException,
)

_CODIGOS_HTTP: dict[type, int] = {
    ValidacionException: 422,
    CredencialesInvalidasException: 401,
    AccesoDenegadoException: 403,
    RecursoNoEncontradoException: 404,
    TransicionEstadoInvalidaException: 409,
}

_logger = logging.getLogger("sistema_incidencias")


def registrar_manejadores_de_error(app: FastAPI) -> None:
    """Traduce la jerarquia de AppException (app/exceptions) a respuestas HTTP consistentes."""

    @app.exception_handler(AppException)
    def _manejar_app_exception(request: Request, exc: AppException) -> JSONResponse:
        status_code = _CODIGOS_HTTP.get(type(exc), 400)
        return JSONResponse(status_code=status_code, content={"error": exc.codigo, "mensaje": exc.mensaje})

    @app.exception_handler(Exception)
    def _manejar_error_inesperado(request: Request, exc: Exception) -> JSONResponse:
        _logger.exception("Error no controlado procesando %s", request.url)
        return JSONResponse(
            status_code=500, content={"error": "ERROR_INTERNO", "mensaje": "Ocurrio un error inesperado"}
        )
