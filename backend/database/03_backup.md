# Estrategia de copias de respaldo (RNF1)

La base `sistema_incidencias_ucv` corre en modo de recuperacion `FULL` para permitir respaldos de log y restauracion punto-en-el-tiempo. Tres tipos de backup, programados con SQL Server Agent (o el Programador de tareas de Windows si se usa SQL Server Express sin Agent):

| Tipo | Frecuencia | Retencion |
|---|---|---|
| Completo (`FULL`) | Diario, 2:00 a.m. | 14 dias |
| Diferencial | Cada 6 horas | 3 dias |
| Log de transacciones | Cada 15 minutos | 3 dias |

## Comandos T-SQL base

```sql
-- Respaldo completo
BACKUP DATABASE sistema_incidencias_ucv
TO DISK = 'C:\Backups\sistema_incidencias_ucv_full.bak'
WITH INIT, COMPRESSION;

-- Respaldo diferencial
BACKUP DATABASE sistema_incidencias_ucv
TO DISK = 'C:\Backups\sistema_incidencias_ucv_diff.bak'
WITH DIFFERENTIAL, COMPRESSION;

-- Respaldo de log (requiere modo FULL)
BACKUP LOG sistema_incidencias_ucv
TO DISK = 'C:\Backups\sistema_incidencias_ucv_log.trn';
```

## Restauracion

```sql
RESTORE DATABASE sistema_incidencias_ucv
FROM DISK = 'C:\Backups\sistema_incidencias_ucv_full.bak'
WITH NORECOVERY;

RESTORE DATABASE sistema_incidencias_ucv
FROM DISK = 'C:\Backups\sistema_incidencias_ucv_diff.bak'
WITH RECOVERY;
```

## Evidencias fotograficas

Los archivos subidos por `EvidenciaService`/`FileStorage` se guardan en disco (fuera de la base de datos, solo se persiste la URL). Deben incluirse en el respaldo del sistema de archivos del servidor (no lo cubre `BACKUP DATABASE`), con la misma frecuencia que el respaldo diferencial.
