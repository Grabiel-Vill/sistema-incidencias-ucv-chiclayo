-- Permite tipo_falla NULL en incidencias: una solicitud de apertura anticipada de laboratorio
-- no es una falla tecnica, asi que no deberia obligar a elegir una categoria de falla.
-- El CHECK existente (tipo_falla IN (...)) sigue aplicando solo cuando el valor no es NULL
-- (asi funciona un CHECK en SQL Server: NULL nunca lo viola), asi que no hace falta tocarlo.
-- Idempotente: ejecutar ALTER COLUMN ... NULL cuando ya es NULL no genera error.

USE sistema_incidencias_ucv;
GO

ALTER TABLE dbo.incidencias ALTER COLUMN tipo_falla VARCHAR(20) NULL;
GO
