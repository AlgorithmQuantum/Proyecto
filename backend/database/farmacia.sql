USE CentroMedicoRASA;
GO

-- ============================================
-- TABLAS DE HISTORIAL Y PEDIDOS (FARMACIA)
-- ============================================

-- 1. Tabla para registrar TODO el historial de movimientos de inventario (Kardex)
CREATE TABLE BITACORA_FARMACIA (
    Id_movimiento      INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    Id_medicamento     INT NOT NULL,
    Id_usuario         INT NOT NULL,         -- El farmacéutico que realizó la acción
    Tipo_movimiento    VARCHAR(50) NOT NULL, -- 'ENTRADA PROVEEDOR', 'VENTA LIBRE', 'SURTIDO RECETA', 'MERMA'
    Cantidad           INT NOT NULL,         -- Positivo (entradas) o negativo (salidas)
    Folio_Referencia   VARCHAR(50),          -- El folio de la receta (FOL-2026), ticket (TKT-123) o pedido
    Observaciones      VARCHAR(200),         -- Justificación en caso de merma o notas extra
    Fecha_Movimiento   DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (Id_medicamento) REFERENCES MEDICAMENTO(Id_medicamento),
    FOREIGN KEY (Id_usuario) REFERENCES USUARIO(Id_usuario)
);

-- 2. Tabla de cabecera para los Pedidos a Droguería / Proveedor
CREATE TABLE PEDIDO_PROVEEDOR (
    Id_pedido          INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    Folio_Pedido       VARCHAR(50) UNIQUE NOT NULL, -- Generado desde backend Ej: 'ORD-78492-MEX'
    Id_usuario         INT NOT NULL,                -- Farmacéutico que solicita el pedido
    Total_estimado     DECIMAL(10,2),
    Estatus            VARCHAR(20) DEFAULT 'Procesando', -- 'Procesando', 'Aprobado', 'Recibido'
    Fecha_Solicitud    DATETIME DEFAULT GETDATE(),
    Fecha_Entrega      DATETIME NULL,
    
    FOREIGN KEY (Id_usuario) REFERENCES USUARIO(Id_usuario)
);

-- 3. Tabla de detalle para los artículos dentro de cada pedido
CREATE TABLE DETALLE_PEDIDO (
    Id_detalle         INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    Id_pedido          INT NOT NULL,
    Id_medicamento     INT NOT NULL,
    Cantidad           INT NOT NULL,
    Precio_Unitario    MONEY,
    Subtotal           MONEY,
    
    FOREIGN KEY (Id_pedido) REFERENCES PEDIDO_PROVEEDOR(Id_pedido),
    FOREIGN KEY (Id_medicamento) REFERENCES MEDICAMENTO(Id_medicamento)
);
GO


USE CentroMedicoRASA;
GO

CREATE TRIGGER trg_IngresarPedidoFarmacia
ON PEDIDO_PROVEEDOR
AFTER UPDATE
AS
BEGIN
    -- Validamos que no se active si no hay filas afectadas para evitar procesamiento innecesario
    IF @@ROWCOUNT = 0 RETURN;

    -- Solo ejecutamos la lógica si la columna 'Estatus' fue parte del UPDATE
    IF UPDATE(Estatus)
    BEGIN
        -- 1. Actualizar el Stock en la tabla MEDICAMENTO sumando las cantidades del pedido
        UPDATE M
        SET M.Stock = M.Stock + DP.Cantidad
        FROM MEDICAMENTO M
        INNER JOIN DETALLE_PEDIDO DP ON M.Id_medicamento = DP.Id_medicamento
        INNER JOIN inserted i ON DP.Id_pedido = i.Id_pedido
        INNER JOIN deleted d ON i.Id_pedido = d.Id_pedido
        -- Condición clave: El estatus nuevo es 'Recibido' y el estatus anterior NO era 'Recibido'
        WHERE i.Estatus = 'Recibido' AND d.Estatus <> 'Recibido';

        -- 2. Insertar automáticamente el movimiento en la BITACORA_FARMACIA para la auditoría
        INSERT INTO BITACORA_FARMACIA (
            Id_medicamento, 
            Id_usuario, 
            Tipo_movimiento, 
            Cantidad, 
            Folio_Referencia, 
            Observaciones
        )
        SELECT 
            DP.Id_medicamento,
            i.Id_usuario,
            'ENTRADA PROVEEDOR',
            DP.Cantidad,
            i.Folio_Pedido,
            'Reabastecimiento automático por pedido recibido'
        FROM DETALLE_PEDIDO DP
        INNER JOIN inserted i ON DP.Id_pedido = i.Id_pedido
        INNER JOIN deleted d ON i.Id_pedido = d.Id_pedido
        WHERE i.Estatus = 'Recibido' AND d.Estatus <> 'Recibido';
    END
END;
GO