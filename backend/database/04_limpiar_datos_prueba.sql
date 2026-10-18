-- Limpia TODOS los datos acumulados (usuarios, laboratorios, incidencias, notas, evidencias,
-- notificaciones, calificaciones, reportes) y deja la base exactamente como recien instalada:
-- solo el administrador semilla (admin@ucv.edu.pe / Admin123), "Lab Computo 1" y "EQ-001".
--
-- DESTRUCTIVO: borra TODO excepto ese seed. No hay vuelta atras (no es soft-delete).
-- Ejecutar conectado a la base 'sistema_incidencias_ucv'.

USE sistema_incidencias_ucv;
GO

-- 1) Borrar en orden hijo -> padre (respeta las foreign keys).
DELETE FROM calificaciones;
DELETE FROM notas_tecnicas;
DELETE FROM evidencias;
DELETE FROM notificaciones;
DELETE FROM incidencias;
DELETE FROM equipos;
DELETE FROM laboratorios;
DELETE FROM usuarios;
DELETE FROM reportes;
GO

-- 2) Reiniciar los contadores IDENTITY a 0 para que el proximo insert arranque en 1
--    (mismos ids que tendria una instalacion nueva desde 01_schema.sql).
DBCC CHECKIDENT ('calificaciones', RESEED, 0);
DBCC CHECKIDENT ('notas_tecnicas', RESEED, 0);
DBCC CHECKIDENT ('evidencias', RESEED, 0);
DBCC CHECKIDENT ('notificaciones', RESEED, 0);
DBCC CHECKIDENT ('incidencias', RESEED, 0);
DBCC CHECKIDENT ('equipos', RESEED, 0);
DBCC CHECKIDENT ('laboratorios', RESEED, 0);
DBCC CHECKIDENT ('usuarios', RESEED, 0);
DBCC CHECKIDENT ('reportes', RESEED, 0);
GO

-- 3) Reinsertar el seed original (identico a 02_seed.sql).
INSERT INTO usuarios (codigo_ucv, nombre, apellido, email, password_hash, rol, estado)
VALUES (
    'A001',
    'Administrador',
    'UCV',
    'admin@ucv.edu.pe',
    'pbkdf2_sha256$390000$5bf82069389264408d57dd9199d563e8$d575d7915c7d0a0968bb74b5d527d2bca401a7a8e5ed96f95fd804e97229b927',
    'ADMINISTRADOR',
    1
);
GO

INSERT INTO laboratorios (nombre, pabellon, piso, estado_operativo)
VALUES ('Lab Computo 1', 'A', 2, 1);
GO

INSERT INTO equipos (id_laboratorio, codigo_patrimonial, tipo_equipo, estado)
SELECT id_laboratorio, 'EQ-001', 'Proyector', 'OPERATIVO'
FROM laboratorios WHERE nombre = 'Lab Computo 1';
GO
