-- TRIGGER 1: Se dispara al agendar una nueva cita (INSERT)
CREATE OR ALTER TRIGGER trg_Cita_Insert
ON CITA
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO BITACORA_CITA (Id_cita, Id_Recepcionista, Estatus_cita, Monto_devuelto, Inicio, Fin, Fecha_cambio)
    SELECT 
        i.Id_cita, 
        1, -- ID genérico o de sistema
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
    
    -- Solo insertar en bitácora si el estatus realmente cambió
    IF UPDATE(Estatus)
    BEGIN
        INSERT INTO BITACORA_CITA (Id_cita, Id_Recepcionista, Estatus_cita, Monto_devuelto, Inicio, Fin, Fecha_cambio)
        SELECT 
            i.Id_cita, 
            1, 
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