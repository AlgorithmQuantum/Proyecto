-- TRIGGER 1: Se dispara al agendar una nueva cita (INSERT)
CREATE OR ALTER TRIGGER trg_Cita_Insert
ON CITA  
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Id_Recepcionista_Actual INT = ISNULL(CAST(SESSION_CONTEXT(N'Id_Recepcionista_actual') AS INT), 1);
     
    INSERT INTO BITACORA_CITA (Id_cita, Id_Recepcionista, Estatus_cita, Monto_devuelto, Inicio, Fin, Fecha_cambio)
    SELECT 
        i.Id_cita, 
        @Id_Recepcionista_Actual,
        i.Estatus, 
        0.00, -- No hay devolución al crear
        i.hora_cita, 
        ISNULL(i.Hora_Fin, i.hora_cita),
        GETDATE()
    FROM inserted i;
END;
GO

-- TRIGGER 2: Se dispara al modificar/cancelar una cita (UPDATE)
CREATE OR ALTER TRIGGER trg_Cita_Update
ON CITA
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Id_Recepcionista_Actual INT = ISNULL(CAST(SESSION_CONTEXT(N'Id_Recepcionista_actual') AS INT), 1);
    
    -- Solo insertar en bitácora si el estatus realmente cambió
    IF UPDATE(Estatus)
    BEGIN
        INSERT INTO BITACORA_CITA (Id_cita, Id_Recepcionista, Estatus_cita, Monto_devuelto, Inicio, Fin, Fecha_cambio)
        SELECT 
            i.Id_cita, 
            @Id_Recepcionista_Actual, 
            i.Estatus, 
            0.00, -- El monto devuelto se actualiza desde el backend
            i.hora_cita, 
            ISNULL(i.Hora_Fin, i.hora_cita),
            GETDATE()
        FROM inserted i
        INNER JOIN deleted d ON i.Id_cita = d.Id_cita
        WHERE i.Estatus <> d.Estatus; -- Condición de cambio
    END
END;
GO

-- TRIGGER 3: Se dispara al eliminar físicamente una cita (DELETE)
CREATE OR ALTER TRIGGER trg_Cita_Delete
ON CITA
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Id_Recepcionista_Actual INT = ISNULL(CAST(SESSION_CONTEXT(N'Id_Recepcionista_actual') AS INT), 1);
    
    INSERT INTO BITACORA_CITA (Id_cita, Id_Recepcionista, Estatus_cita, Monto_devuelto, Inicio, Fin, Fecha_cambio)
    SELECT 
        d.Id_cita, 
        @Id_Recepcionista_Actual, 
        0, -- 0 representa que la cita fue anulada/eliminada
        0.00, 
        d.hora_cita, 
        ISNULL(d.Hora_Fin, d.hora_cita),
        GETDATE()
    FROM deleted d;
END;
GO