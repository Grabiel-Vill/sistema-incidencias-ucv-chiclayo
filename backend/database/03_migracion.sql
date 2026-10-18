-- Migracion idempotente: agrega SOFTWARE al tipo de falla, columna subcategoria en incidencias,
-- columna prioridad en notificaciones (campana de prioridad ALTA) y la tabla calificaciones.
-- Seguro de re-ejecutar: cada cambio esta protegido por un IF NOT EXISTS / comprobacion previa.
-- Ejecutar conectado a la base 'sistema_incidencias_ucv' (despues de 01_schema.sql/02_seed.sql).

USE sistema_incidencias_ucv;
GO

-- 1) Agrega SOFTWARE al CHECK de tipo_falla sin asumir el nombre autogenerado del constraint.
DECLARE @constraint_name NVARCHAR(200);
SELECT @constraint_name = cc.name
FROM sys.check_constraints cc
WHERE cc.parent_object_id = OBJECT_ID('dbo.incidencias')
  AND cc.definition LIKE '%tipo_falla%'
  AND cc.definition NOT LIKE '%SOFTWARE%';

IF @constraint_name IS NOT NULL
BEGIN
    EXEC('ALTER TABLE dbo.incidencias DROP CONSTRAINT ' + @constraint_name);
    EXEC('ALTER TABLE dbo.incidencias ADD CONSTRAINT CK_incidencias_tipo_falla '
        + 'CHECK (tipo_falla IN (''HARDWARE'',''RED'',''SOFTWARE'',''ELECTRICIDAD'',''ILUMINACION''))');
END
GO

-- 2) Columna subcategoria (catalogo UI, ver app/utils/catalogo_incidencias.py).
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.incidencias') AND name = 'subcategoria')
BEGIN
    ALTER TABLE dbo.incidencias ADD subcategoria VARCHAR(80) NULL;
END
GO

-- 3) Columna prioridad en notificaciones, para que la campana del tecnico resalte asignaciones ALTA.
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.notificaciones') AND name = 'prioridad')
BEGIN
    ALTER TABLE dbo.notificaciones ADD prioridad VARCHAR(10) NULL;
END
GO

-- 4) Tabla calificaciones: una calificacion (1-5 estrellas) por incidencia resuelta.
IF OBJECT_ID('dbo.calificaciones', 'U') IS NULL
BEGIN
    CREATE TABLE calificaciones (
        id_calificacion INT IDENTITY(1,1) PRIMARY KEY,
        id_incidencia   INT          NOT NULL UNIQUE REFERENCES incidencias(id_incidencia),
        id_docente      INT          NOT NULL REFERENCES usuarios(id_usuario),
        id_tecnico      INT          NOT NULL REFERENCES usuarios(id_usuario),
        estrellas       INT          NOT NULL CHECK (estrellas BETWEEN 1 AND 5),
        comentario      VARCHAR(500) NULL,
        fecha           DATETIME2    NOT NULL DEFAULT SYSDATETIME()
    );
END
GO
