USE CentroMedicoRASA;
GO

-- ============================================================
-- Funcion: Verifica si el doctor tiene otra cita a esa hora (Cero empalmes)
-- ============================================================
CREATE OR ALTER FUNCTION fn_DoctorDisponible
(
    @Id_doctor  INT,
    @Fecha_cita DATE,
    @Hora_cita  TIME
)
RETURNS BIT
AS
BEGIN
    DECLARE @Disponible BIT;

    -- Revisa si ya existe una cita activa para ese doctor, ese día y a esa hora
    IF EXISTS (
        SELECT 1
        FROM CITA
        WHERE Id_doctor = @Id_doctor
          AND Fecha_cita = @Fecha_cita
          AND hora_cita = @Hora_cita
          AND Estatus = 1
    )
        SET @Disponible = 0; -- Ocupado
    ELSE
        SET @Disponible = 1; -- Disponible

    RETURN @Disponible;
END;
GO

-- ============================================================
-- Procedimiento: Agendar cita
-- ============================================================
USE CentroMedicoRASA;
GO

CREATE OR ALTER PROCEDURE sp_CrearCita
    @Id_paciente        INT,
    @Id_doctor          INT,
    @Id_consultorio     INT,
    @Fecha_cita         DATE,
    @Hora_cita          TIME,
    @Hora_Fin           TIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Dia        INT      = DAY(@Fecha_cita);
    DECLARE @Mes        INT      = MONTH(@Fecha_cita);
    DECLARE @Ahora      DATETIME = GETDATE();
    DECLARE @FechaHora  DATETIME = CAST(@Fecha_cita AS DATETIME) + CAST(@Hora_cita  AS DATETIME);

    -- [VALIDACIÓN PREVIA EXISTENTE] Fechas pasadas
    IF @FechaHora <= @Ahora
    BEGIN
        RAISERROR('No se pueden agendar citas en una fecha y hora pasada.', 16, 1);
        RETURN;
    END

    -- [NUEVO] Cambio de 48 horas exactas a "Mínimo al día siguiente (24 hrs lógicas)"
    IF DATEDIFF(DAY, CAST(@Ahora AS DATE), @Fecha_cita) < 1
    BEGIN
        RAISERROR('La cita debe agendarse al menos para el día de mañana.', 16, 2);
        RETURN;
    END

    -- [VALIDACIÓN PREVIA EXISTENTE] Ventana de 3 meses
    IF @FechaHora > DATEADD(MONTH, 3, @Ahora)
    BEGIN
        RAISERROR('No se pueden agendar citas con más de 3 meses de anticipación.', 16, 3);
        RETURN;
    END

    -- Existencia de entidades
    IF NOT EXISTS (SELECT 1 FROM PACIENTE WHERE Id_paciente = @Id_paciente)
    BEGIN
        RAISERROR('El paciente no existe.', 16, 4);
        RETURN;
    END

    --  Bloqueo de múltiples citas activas/pendientes
    IF EXISTS (
        SELECT 1 
        FROM CITA 
        WHERE Id_paciente = @Id_paciente 
          AND Estatus = 1 
          AND Id_receta IS NULL
    )
    BEGIN
        RAISERROR('Ya tienes una cita agendada pendiente de atención. Debes concluirla o cancelarla antes de poder agendar una nueva.', 16, 8);
        RETURN;
    END

    IF NOT EXISTS (SELECT 1 FROM DOCTOR WHERE Id_doctor = @Id_doctor)
    BEGIN
        RAISERROR('El doctor no existe.', 16, 5);
        RETURN;
    END

    IF NOT EXISTS (SELECT 1 FROM CONSULTORIO WHERE Id_consultorio = @Id_consultorio)
    BEGIN
        RAISERROR('El consultorio no existe.', 16, 6);
        RETURN;
    END

    -- Validación 1: Revisar empalmes con otras citas
    IF dbo.fn_DoctorDisponible(@Id_doctor, @Fecha_cita, @Hora_cita) = 0
    BEGIN
        RAISERROR('El doctor ya tiene una cita ocupada en ese horario exacto.', 16, 7);
        RETURN;
    END

    -- Validación 2: Revisar turno y día de trabajo del doctor
    DECLARE @NumDia INT;
    DECLARE @DiaElegido NVARCHAR(20);
    SET @NumDia = DATEDIFF(DAY, '19000101', @Fecha_cita) % 7;

    SET @DiaElegido = CASE @NumDia
        WHEN 0 THEN 'Lunes'
        WHEN 1 THEN 'Martes'
        WHEN 2 THEN 'Miércoles'
        WHEN 3 THEN 'Jueves'
        WHEN 4 THEN 'Viernes'
        WHEN 5 THEN 'Sábado'
        WHEN 6 THEN 'Domingo'
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM DOCTOR d
        JOIN EMPLEADO_HORARIO eh ON d.Id_empleado = eh.Id_empleado
        JOIN HORARIO h ON eh.Id_Horario = h.Id_Horario
        WHERE d.Id_doctor = @Id_doctor
            AND h.Dia COLLATE Latin1_General_CI_AI = @DiaElegido 
            AND @Hora_cita >= h.Hora_Inicio 
            AND @Hora_Fin <= h.Hora_Fin
    )
    BEGIN
        RAISERROR ('El horario elegido no corresponde a los días o turnos de atención del doctor.', 16, 1);
        RETURN;
    END

    -- Cita válida
    INSERT INTO CITA (
        Id_paciente, Id_doctor, Id_consultorio, Id_receta,
        Fecha_cita, hora_cita, Dia, Mes, Estatus, Hora_Fin
    )
    VALUES (
        @Id_paciente, @Id_doctor, @Id_consultorio, NULL,           
        @Fecha_cita, @Hora_cita, @Dia, @Mes, 1, @Hora_Fin
    );

    PRINT 'Cita agendada exitosamente.';
END;
GO

-- ============================================================
-- Procedimiento: Actualizar citas expiradas 
-- ============================================================
CREATE OR ALTER PROCEDURE sp_ActualizarCitasExpiradas
AS
BEGIN
    SET NOCOUNT ON;

    -- Si la fecha ya pasó y el doctor nunca le asignó una receta,
    -- desactivamos el estatus de la cita (Estatus = 0) para marcar que expiró.
    UPDATE CITA
    SET Estatus = 0
    WHERE Fecha_cita < CAST(GETDATE() AS DATE)
      AND Estatus = 1
      AND Id_receta IS NULL;

    PRINT 'Citas vencidas actualizadas a (No acudió) correctamente.';
END;
GO

-- ============================================================
-- FUNCIONES DEL SISTEMA
-- ============================================================

--========================================================
--Funcion: Calcula el total usando la cantidad y el costo real del servicio.
--========================================================
CREATE OR ALTER FUNCTION FN_TotalServicios
(
    @IdCita INT
)
RETURNS DECIMAL(10,2)
AS
BEGIN
    DECLARE @ResultVar DECIMAL(10,2);

    SELECT @ResultVar =
        SUM(CS.Cantidad * S.Costo)
    FROM CITA_SERVICIO CS
    INNER JOIN SERVICIO S
        ON CS.Id_servicio = S.Id_servicio
    WHERE CS.Id_cita = @IdCita;

    RETURN ISNULL(@ResultVar,0);
END;
GO

--========================================================
--Funcion: Obtiene la cantidad total de medicamentos prescritos en una receta.
--========================================================
CREATE OR ALTER FUNCTION FN_TotalMedicamentosReceta
(
    @IdReceta INT
)
RETURNS INT
AS
BEGIN
    DECLARE @ResultVar INT;

    SELECT @ResultVar =
        SUM(Cantidad)
    FROM RECETA_MEDICINA
    WHERE Id_receta = @IdReceta;

    RETURN ISNULL(@ResultVar,0);
END;
GO

--========================================================
--Funcion: Cuenta cuántos pacientes diferentes ha atendido un doctor mediante las citas activas.
--========================================================
CREATE OR ALTER FUNCTION FN_PacientesAtendidosDoctor
(
    @IdDoctor INT
)
RETURNS INT
AS
BEGIN
    DECLARE @ResultVar INT;

    SELECT @ResultVar =
        COUNT(DISTINCT Id_paciente)
    FROM CITA
    WHERE Id_doctor = @IdDoctor
      AND Estatus = 1;

    RETURN ISNULL(@ResultVar,0);
END;
GO

-- ============================================================
-- PRUEBAS DE FUNCIONES (AHORA CORRECTAMENTE SEPARADAS)
-- ============================================================

-- Prueba de FN_TotalServicios
SELECT dbo.FN_TotalServicios(1) AS TotalServicios;
GO

-- Prueba de FN_TotalMedicamentosReceta
SELECT dbo.FN_TotalMedicamentosReceta(1) AS TotalMedicamentos;
GO

-- Prueba de FN_PacientesAtendidosDoctor
SELECT dbo.FN_PacientesAtendidosDoctor(2) AS PacientesAtendidos;
GO

-- ============================================================
-- VISTAS DEL SISTEMA
-- ============================================================

-- Detalle de Citas del Paciente
CREATE OR ALTER VIEW VW_Detalle_Cita_Paciente
AS
SELECT
    C.Id_cita,
    C.Id_paciente,
    P.Nombre + ' ' + P.Apellido_Paterno + ' ' + ISNULL(P.Apellido_Materno, '') AS Paciente,
    C.Fecha_cita,
    C.hora_cita,
    C.Hora_Fin,
    C.Estatus,
    D.Id_doctor,
    E.Nombre + ' ' + E.Apellido_Paterno AS Doctor,
    ES.Nombre AS Especialidad,
    ES.Costo_Consulta,
    CO.Numero AS Consultorio,
    CO.Piso,
    R.Diagnostico,
    ISNULL((SELECT TOP 1 Estatus_pago FROM TICKET T WHERE T.Id_cita = C.Id_cita), 'Pendiente') AS Estatus_Pago
FROM CITA C
INNER JOIN PACIENTE P ON C.Id_paciente = P.Id_paciente
INNER JOIN DOCTOR D ON C.Id_doctor = D.Id_doctor
INNER JOIN EMPLEADO E ON D.Id_empleado = E.Id_empleado
INNER JOIN ESPECIALIDAD ES ON D.Id_especialidad = ES.Id_especialidad
LEFT JOIN CONSULTORIO CO ON C.Id_consultorio = CO.Id_consultorio
LEFT JOIN RECETA R ON C.Id_receta = R.Id_receta;
GO

-- Historial Médico del Paciente
CREATE OR ALTER VIEW VW_Historial_Medico
AS
SELECT
    P.Id_paciente,
    P.Nombre,
    P.Apellido_Paterno,
    HM.Id_historial,
    HM.Tipo_sangre,
    HM.Estatura,
    HM.Peso,
    HM.Edad,
    HM.Alergias
FROM PACIENTE P
INNER JOIN HISTORIA_MEDICO HM ON P.Id_paciente = HM.Id_paciente;
GO

-- Detalle de Pagos
CREATE OR ALTER VIEW VW_Detalle_Pagos
AS
SELECT
    PG.Id_pago,
    PG.Fecha_pago,
    PG.Monto,
    PG.Linea_pago,
    PG.Estatus,
    C.Id_cita,
    P.Nombre + ' ' + P.Apellido_Paterno AS Paciente,
    E.Nombre + ' ' + E.Apellido_Paterno AS Doctor
FROM PAGO PG
INNER JOIN CITA C ON PG.Id_cita = C.Id_cita
INNER JOIN PACIENTE P ON C.Id_paciente = P.Id_paciente
INNER JOIN DOCTOR D ON C.Id_doctor = D.Id_doctor
INNER JOIN EMPLEADO E ON D.Id_empleado = E.Id_empleado;
GO

-- Actividad de Doctores
CREATE OR ALTER VIEW VW_Actividad_Doctor
AS
SELECT
    D.Id_doctor,
    E.Nombre + ' ' + E.Apellido_Paterno AS Doctor,
    ES.Nombre AS Especialidad,
    COUNT(C.Id_cita) AS Total_Citas
FROM DOCTOR D
INNER JOIN EMPLEADO E ON D.Id_empleado = E.Id_empleado
INNER JOIN ESPECIALIDAD ES ON D.Id_especialidad = ES.Id_especialidad
LEFT JOIN CITA C ON D.Id_doctor = C.Id_doctor
GROUP BY D.Id_doctor, E.Nombre, E.Apellido_Paterno, ES.Nombre;
GO