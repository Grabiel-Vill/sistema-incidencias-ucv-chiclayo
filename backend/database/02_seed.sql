-- Datos iniciales: un administrador, un laboratorio y un equipo de ejemplo.
-- Ejecutar DESPUES de 01_schema.sql, conectado a la base 'sistema_incidencias_ucv'.
--
-- El password_hash del administrador ya viene calculado con el mismo algoritmo que usa la
-- app (PasswordHasher: PBKDF2-HMAC-SHA256), porque SQL Server no puede replicarlo en T-SQL.
-- Contrasena en texto plano para este usuario semilla: Admin123

USE sistema_incidencias_ucv;
GO

IF NOT EXISTS (SELECT 1 FROM usuarios WHERE email = 'admin@ucv.edu.pe')
BEGIN
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
END
GO

IF NOT EXISTS (SELECT 1 FROM laboratorios WHERE nombre = 'Lab Computo 1')
BEGIN
    INSERT INTO laboratorios (nombre, pabellon, piso, estado_operativo)
    VALUES ('Lab Computo 1', 'A', 2, 1);
END
GO

IF NOT EXISTS (SELECT 1 FROM equipos WHERE codigo_patrimonial = 'EQ-001')
BEGIN
    INSERT INTO equipos (id_laboratorio, codigo_patrimonial, tipo_equipo, estado)
    SELECT id_laboratorio, 'EQ-001', 'Proyector', 'OPERATIVO'
    FROM laboratorios WHERE nombre = 'Lab Computo 1';
END
GO
