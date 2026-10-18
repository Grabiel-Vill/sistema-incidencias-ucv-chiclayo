-- Script de creacion de tablas SQL Server para el Sistema de Incidencias UCV Chiclayo.
-- Ejecutar conectado como un usuario con permiso para crear bases de datos (ej. sa).

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'sistema_incidencias_ucv')
BEGIN
    CREATE DATABASE sistema_incidencias_ucv;
END
GO

USE sistema_incidencias_ucv;
GO

IF OBJECT_ID('dbo.calificaciones', 'U') IS NOT NULL DROP TABLE dbo.calificaciones;
IF OBJECT_ID('dbo.notificaciones', 'U') IS NOT NULL DROP TABLE dbo.notificaciones;
IF OBJECT_ID('dbo.notas_tecnicas', 'U') IS NOT NULL DROP TABLE dbo.notas_tecnicas;
IF OBJECT_ID('dbo.evidencias', 'U') IS NOT NULL DROP TABLE dbo.evidencias;
IF OBJECT_ID('dbo.incidencias', 'U') IS NOT NULL DROP TABLE dbo.incidencias;
IF OBJECT_ID('dbo.equipos', 'U') IS NOT NULL DROP TABLE dbo.equipos;
IF OBJECT_ID('dbo.laboratorios', 'U') IS NOT NULL DROP TABLE dbo.laboratorios;
IF OBJECT_ID('dbo.reportes', 'U') IS NOT NULL DROP TABLE dbo.reportes;
IF OBJECT_ID('dbo.usuarios', 'U') IS NOT NULL DROP TABLE dbo.usuarios;
GO

-- Usuario (Docente / Tecnico / Administrador) via columna discriminadora 'rol'.
-- especialidad/disponible solo se usan cuando rol = 'TECNICO'.
CREATE TABLE usuarios (
    id_usuario       INT IDENTITY(1,1) PRIMARY KEY,
    codigo_ucv       VARCHAR(20)  NOT NULL UNIQUE,
    nombre           VARCHAR(100) NOT NULL,
    apellido         VARCHAR(100) NOT NULL,
    email            VARCHAR(150) NOT NULL UNIQUE,
    password_hash    VARCHAR(255) NOT NULL,
    rol              VARCHAR(20)  NOT NULL CHECK (rol IN ('DOCENTE', 'TECNICO', 'ADMINISTRADOR')),
    estado           BIT          NOT NULL DEFAULT 1,
    especialidad     VARCHAR(100) NULL,
    disponible       BIT          NULL
);
GO

CREATE TABLE laboratorios (
    id_laboratorio    INT IDENTITY(1,1) PRIMARY KEY,
    nombre            VARCHAR(100) NOT NULL,
    pabellon          VARCHAR(50)  NOT NULL,
    piso              INT          NOT NULL,
    estado_operativo  BIT          NOT NULL DEFAULT 1
);
GO

CREATE TABLE equipos (
    id_equipo           INT IDENTITY(1,1) PRIMARY KEY,
    id_laboratorio      INT          NOT NULL REFERENCES laboratorios(id_laboratorio),
    codigo_patrimonial  VARCHAR(50)  NOT NULL,
    tipo_equipo         VARCHAR(100) NOT NULL,
    estado              VARCHAR(20)  NOT NULL DEFAULT 'OPERATIVO'
                         CHECK (estado IN ('OPERATIVO', 'DEFECTUOSO', 'EN_MANTENIMIENTO'))
);
GO

CREATE TABLE incidencias (
    id_incidencia         INT IDENTITY(1,1) PRIMARY KEY,
    codigo_ticket         VARCHAR(30)  NOT NULL UNIQUE,
    descripcion           VARCHAR(1000) NOT NULL,
    tipo_falla            VARCHAR(20)  NULL
                          CHECK (tipo_falla IN ('HARDWARE', 'RED', 'SOFTWARE', 'ELECTRICIDAD', 'ILUMINACION')),
    tipo_requerimiento    VARCHAR(30)  NOT NULL DEFAULT 'FALLA_TECNICA'
                          CHECK (tipo_requerimiento IN ('FALLA_TECNICA', 'APERTURA_ANTICIPADA')),
    subcategoria          VARCHAR(80)  NULL,
    id_laboratorio        INT          NOT NULL REFERENCES laboratorios(id_laboratorio),
    id_equipo             INT          NULL REFERENCES equipos(id_equipo),
    id_docente            INT          NOT NULL REFERENCES usuarios(id_usuario),
    id_tecnico_asignado   INT          NULL REFERENCES usuarios(id_usuario),
    estado                VARCHAR(20)  NOT NULL DEFAULT 'RECIBIDO'
                          CHECK (estado IN ('RECIBIDO', 'PROGRAMADO', 'EN_PROCESO', 'RESUELTO')),
    prioridad             VARCHAR(10)  NOT NULL DEFAULT 'MEDIA'
                          CHECK (prioridad IN ('ALTA', 'MEDIA', 'BAJA')),
    fecha_creacion        DATETIME2    NOT NULL DEFAULT SYSDATETIME(),
    fecha_atencion        DATETIME2    NULL,
    fecha_resolucion      DATETIME2    NULL,
    fecha_hora_apertura   DATETIME2    NULL
);
GO

CREATE TABLE evidencias (
    id_evidencia     INT IDENTITY(1,1) PRIMARY KEY,
    id_incidencia    INT          NOT NULL REFERENCES incidencias(id_incidencia),
    url_imagen       VARCHAR(500) NOT NULL,
    fecha_carga      DATETIME2    NOT NULL DEFAULT SYSDATETIME()
);
GO

CREATE TABLE notas_tecnicas (
    id_nota          INT IDENTITY(1,1) PRIMARY KEY,
    id_incidencia    INT           NOT NULL REFERENCES incidencias(id_incidencia),
    contenido        VARCHAR(1000) NOT NULL,
    es_privado       BIT           NOT NULL DEFAULT 1,
    fecha_creacion   DATETIME2     NOT NULL DEFAULT SYSDATETIME()
);
GO

CREATE TABLE notificaciones (
    id_notificacion  INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario       INT          NOT NULL REFERENCES usuarios(id_usuario),
    mensaje          VARCHAR(500) NOT NULL,
    tipo             VARCHAR(30)  NOT NULL CHECK (tipo IN ('ASIGNACION', 'CAMBIO_ESTADO')),
    fecha            DATETIME2    NOT NULL DEFAULT SYSDATETIME(),
    leido            BIT          NOT NULL DEFAULT 0,
    prioridad        VARCHAR(10)  NULL
);
GO

CREATE TABLE calificaciones (
    id_calificacion  INT IDENTITY(1,1) PRIMARY KEY,
    id_incidencia    INT          NOT NULL UNIQUE REFERENCES incidencias(id_incidencia),
    id_docente       INT          NOT NULL REFERENCES usuarios(id_usuario),
    id_tecnico       INT          NOT NULL REFERENCES usuarios(id_usuario),
    estrellas        INT          NOT NULL CHECK (estrellas BETWEEN 1 AND 5),
    comentario       VARCHAR(500) NULL,
    fecha            DATETIME2    NOT NULL DEFAULT SYSDATETIME()
);
GO

CREATE TABLE reportes (
    id_reporte        INT IDENTITY(1,1) PRIMARY KEY,
    fecha_generacion  DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO

CREATE INDEX ix_incidencias_estado ON incidencias(estado);
CREATE INDEX ix_incidencias_laboratorio ON incidencias(id_laboratorio);
CREATE INDEX ix_incidencias_docente ON incidencias(id_docente);
CREATE INDEX ix_incidencias_tecnico ON incidencias(id_tecnico_asignado);
CREATE INDEX ix_equipos_laboratorio ON equipos(id_laboratorio);
CREATE INDEX ix_notificaciones_usuario ON notificaciones(id_usuario);
GO
