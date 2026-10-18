# Arquitectura - Sistema de Incidencias Tecnicas UCV Chiclayo
Python + MySQL | MVC + capas (Controller -> Service -> Repository -> Model)

## Flujo
Vista (frontend, vacio por ahora) -> controllers -> services -> repositories -> MySQL
- models: entidades del dominio (M)
- controllers: reciben peticiones y devuelven respuestas (C)
- vistas: frontend (V), vacio por ahora
- dtos: objetos de transferencia entre capas
- services: logica de negocio (incluye DashboardService, ChatbotService, AsistenteIA)
- repositories: acceso a datos (DAO/ORM)

## Cambios respecto al diagrama de clases
- Se elimina la clase Estudiante (no usa el sistema).
- Se agregan: RolEnum, TipoRequerimientoEnum (RF1 apertura anticipada), estado PROGRAMADO,
  TokenDTO, FiltroDTO, MetricasDTO, repositories, middleware, exceptions, utils, integrations.
- ChatbotService, AsistenteIA y DashboardService pasan a la capa services; Reporte queda en models.
- Usuario es clase base; Administrador, Docente y Tecnico heredan de ella.

## Casos de uso -> controller
UC01,02,05,06,07 -> IncidenciaController | UC03,04 -> ChatbotController | UC08 -> NotificacionController
UC09 -> DashboardController | UC10 -> UsuarioController | UC11 -> LaboratorioController/EquipoController
UC12 -> ReporteController | UC13 -> AuthController
