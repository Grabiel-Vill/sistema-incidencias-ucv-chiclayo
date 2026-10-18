# CHANGELOG

Trabajo realizado sobre el sistema existente, en 4 fases (backend transversal → docente →
técnico → admin), más esta fase final de pruebas. No se agregó ninguna tecnología nueva:
backend sigue siendo FastAPI + Python en capas sobre SQL Server (con respaldo en memoria),
frontend sigue siendo JS vanilla con módulos ES, sin frameworks ni bundlers.

## Archivos nuevos

**Backend**
- `app/models/calificacion.py` — entidad Calificacion (1-5 estrellas, por incidencia).
- `app/repositories/calificacion_repository.py`
- `app/services/calificacion_service.py`
- `app/dtos/calificacion_dto.py`
- `app/dtos/sugerencia_ticket_dto.py` — datos que sugiere el chatbot para precargar el form.
- `app/utils/catalogo_incidencias.py` — única fuente categoría→subcategoría→tipo_falla.
- `database/03_migracion.sql` — migración idempotente (SOFTWARE, subcategoria, prioridad en
  notificaciones, tabla calificaciones) para no tener que recrear la BD desde cero.
- `tests/unit/test_reglas_negocio.py` — pruebas de las reglas nuevas contra el repositorio
  en memoria (ver sección Pruebas).

**Frontend**
- `app/vistas/pages/admin-incidencias.html`
- `app/vistas/js/controllers/AdminIncidenciasController.js`

## Archivos modificados (resumen por área)

**Base de datos / arranque**
- `.env`, `app/config/database.py`: conexión a instancia nombrada de SQL Server (la cadena
  de conexión original solo soportaba instancia por defecto con puerto fijo).

**Dominio de incidencias**
- `app/models/enums/tipo_falla_enum.py` (+SOFTWARE), `app/models/incidencia.py` (+subcategoria),
  `app/models/docente.py`, `app/dtos/incidencia_dto.py`, `app/dtos/incidencia_respuesta_dto.py`,
  `app/repositories/incidencia_repository.py`, `app/controllers/incidencia_controller.py`,
  `app/services/incidencia_service.py`.

**Notas técnicas y evidencias**
- `app/services/nota_tecnica_service.py` (valida pertenencia del ticket al técnico),
  `app/controllers/evidencia_controller.py` (+GET para listar), `app/main.py` (monta
  `/storage` como estático para servir las fotos subidas).

**Notificaciones**
- `app/models/notificacion.py`, `app/repositories/notificacion_repository.py`,
  `app/services/notificacion_service.py`, `app/controllers/notificacion_controller.py`:
  campo `prioridad` para que la campana del técnico resalte asignaciones ALTA.

**Chatbot**
- `app/services/chatbot_service.py` (reescrito: ya no crea el ticket solo, devuelve una
  sugerencia para que el docente confirme), `app/dtos/respuesta_ia_dto.py`,
  `app/controllers/chatbot_controller.py`.

**Usuarios**
- `app/dtos/usuario_dto.py` (+especialidad), `app/services/usuario_service.py` (+editar,
  +restablecer_password), `app/controllers/usuario_controller.py`, `app/models/usuario.py`
  (+restablecer_password).

**Dashboard / reportes**
- `app/models/reporte.py`, `app/models/administrador.py`, `app/dtos/metricas_dto.py`,
  `app/services/dashboard_service.py`.

**Wiring**
- `app/main.py`, `app/repositories/__init__.py`, `app/services/__init__.py`.

**Frontend** (la lista completa de componentes/controllers tocados):
`IncidenciaDTO.js`, `IncidenciaRespuestaDTO.js`, `RespuestaIADTO.js`, `NotificacionDTO.js`,
`UsuarioDTO.js`, `MetricasDTO.js`, `Validators.js`, `Icons.js`, `IncidenciaService.js`,
`EvidenciaService.js`, `UsuarioService.js`, `IncidenciaForm.js` (reescrito),
`ChatbotWidget.js`, `IncidenciaTable.js`, `StatusBadge.js`, `NotificationBell.js`,
`DocentePanelController.js` (reescrito), `TecnicoBandejaController.js` (reescrito),
`AdminUsuariosController.js`, `AdminLaboratoriosController.js`, `AdminDashboardController.js`,
`Sidebar.js`, `docente-panel.html`, `tecnico-bandeja.html`, `admin-usuarios.html`,
`admin-laboratorios.html`, `base.css`, `components.css`.

## Cambios de base de datos

Reflejados en `01_schema.sql` (instalación nueva) y `03_migracion.sql` (instalación existente):

- `incidencias.subcategoria VARCHAR(80) NULL`
- CHECK de `incidencias.tipo_falla` ampliado con `SOFTWARE`
- `notificaciones.prioridad VARCHAR(10) NULL`
- Tabla nueva `calificaciones` (id_incidencia UNIQUE, id_docente, id_tecnico, estrellas 1-5,
  comentario, fecha)

## Endpoints nuevos

| Método | Ruta | Rol |
|---|---|---|
| GET | `/incidencias/catalogo` | cualquier autenticado |
| GET | `/incidencias/mis-metricas` | técnico |
| GET | `/incidencias/tecnicos/carga` | admin |
| GET | `/incidencias/{id}/evidencias` | cualquier autenticado |
| POST | `/incidencias/{id}/calificacion` | docente |
| PUT | `/usuarios/{id}` | admin |
| POST | `/usuarios/{id}/restablecer-password` | admin |
| GET | `/storage/...` | estático, sirve las fotos de evidencia |

## Endpoints con cambio de comportamiento (misma ruta, sin romper contrato existente)

- `POST /incidencias/{id}/asignar`: ahora recibe también `prioridad`, pasa el ticket a
  PROGRAMADO y notifica al técnico **y** al docente (antes solo asignaba y notificaba al técnico).
- `GET /incidencias`: si quien llama es TECNICO, el backend fuerza `id_tecnico` al propio
  usuario sin importar lo que mande el cliente (ver "Fallas de seguridad corregidas").
- `PATCH /incidencias/{id}/estado`: valida que el ticket este asignado al técnico que llama,
  y exige una nota pública antes de permitir RESUELTO.
- `POST /incidencias/{id}/notas`: valida que el ticket esté asignado al técnico que llama.
- `POST /chatbot/mensaje`: ya no crea un ticket automáticamente; devuelve
  `requiere_atencion_fisica` + `sugerencia_ticket` para que el docente confirme desde el form.
- `POST /incidencias`: acepta `subcategoria`, rechaza laboratorios en mantenimiento y fechas
  de apertura anticipada no futuras.
- `GET /dashboard/metricas`: incluye `evaluacion_promedio_tecnicos` y `puntualidad_apertura`
  (antes este último campo existía en el DTO pero nunca se calculaba).
- `GET /usuarios`: incluye `especialidad`.

## Fallas de seguridad encontradas y corregidas

Encontradas durante el desarrollo del panel técnico/admin, no estaban en el alcance original
pero violaban la regla de "seguridad en backend, no solo en la interfaz":

1. Cualquier técnico podía ver los tickets de **otros** técnicos (`GET /incidencias` no
   forzaba el filtro `id_tecnico`).
2. Cualquier técnico podía cambiar el estado de un ticket **no asignado a él**.
3. Cualquier técnico podía agregar notas a un ticket **no asignado a él**.

Las tres corregidas a nivel de servicio (`IncidenciaService`, `NotaTecnicaService`), con
pruebas automatizadas que las cubren.

## Otros bugs encontrados y corregidos en el camino

- Campo oculto con `elemento.hidden = true` no se ocultaba porque `.campo-formulario` fuerza
  `display: flex` (el atributo `hidden` nativo queda anulado por cualquier regla de `display`
  del autor). Corregido con una clase utilitaria `.oculto { display: none !important }`,
  usada en el formulario de incidencia (fecha de apertura anticipada) y en alta de usuarios
  (especialidad del técnico).
- `.modal-caja` no tenía `max-height`/`overflow-y`: con contenido largo (detalle del técnico)
  el botón de guardar quedaba fuera de la pantalla sin forma de hacer scroll.
- `DashboardService` usaba `if self._calificaciones else None`: como `BaseRepository` define
  `__len__`, un repositorio SQL con el diccionario en memoria vacío (`_usa_sql=True` no usa
  ese diccionario) se evalúa como **falso** aunque el objeto exista y funcione. Esto ocultaba
  la evaluación promedio de técnicos aunque hubiera calificaciones reales en la BD.
- En `AdminLaboratoriosController`, guardar cambios de nombre/pabellón/piso reconstruía el
  DTO sin pasar `estadoOperativo`, reactivando silenciosamente un laboratorio en mantenimiento.
- `{ ...tecnico }` (spread) perdía el getter `nombreCompleto` de `UsuarioDTO` (el spread solo
  copia propiedades propias, no getters del prototipo de la clase) — el nombre del técnico
  sugerido salía `undefined` en el modal de asignación.

## Pruebas

`backend/tests/unit/test_reglas_negocio.py` — script simple sin dependencias nuevas (no se
agregó pytest), corre con `python tests/unit/test_reglas_negocio.py` contra repositorios
100% en memoria. 9/9 pasan:

- Registro con apertura anticipada sin fecha → rechazo
- Resolver un ticket sin nota pública → rechazo
- Resolver con nota pública → funciona
- Calificar un ticket no resuelto → rechazo
- Calificar un ticket ajeno (otro docente) → rechazo
- Calificar dos veces el mismo ticket → rechazo
- Docente no ve notas privadas (sí ve las públicas; técnico ve ambas)
- Técnico no puede operar un ticket no asignado a él
- Laboratorio en mantenimiento rechaza tickets nuevos

Además, cada pantalla (login, panel docente, bandeja técnica, dashboard admin, gestión de
incidencias, usuarios, laboratorios, reportes) se verificó en navegador real (Playwright,
no solo lectura de código) en viewport de escritorio y móvil, sin errores de consola
reales — los únicos 404 observados son el logo opcional del login, que ya era un
comportamiento intencional preexistente.

## No incluido / fuera de alcance de esta entrega

- `docs/ARQUITECTURA.md` sigue mencionando MySQL; el proyecto en realidad corre sobre SQL
  Server (inconsistencia preexistente, no se tocó).
- No se armó un .zip de entrega (el usuario ya tiene el proyecto en su máquina).
