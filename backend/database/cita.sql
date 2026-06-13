USE CentroMedicoRASA;
GO

-- ============================================================
-- Funcion: Verifica si la cita es en el horario del doctor
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
    DECLARE @Disponible BIT = 0;
    DECLARE @DiaSemana VARCHAR(20);

    -- Asegura el mapeo correcto independientemente del idioma del servidor
    SET @DiaSemana = CASE DATEPART(WEEKDAY, @Fecha_cita)
        WHEN 1 THEN 'Domingo'
        WHEN 2 THEN 'Lunes'
        WHEN 3 THEN 'Martes'
        WHEN 4 THEN 'Miércoles'
        WHEN 5 THEN 'Jueves'
        WHEN 6 THEN 'Viernes'
        WHEN 7 THEN 'Sábado'
    END;

    -- Verifica que el dia y la hora esten dentro del horario del doctor
    IF EXISTS (
        SELECT 1
        FROM DOCTOR D
        INNER JOIN HORARIO H ON D.Id_Horario = H.Id_Horario
        WHERE D.Id_doctor   = @Id_doctor
          AND H.Dia         = @DiaSemana
          AND @Hora_cita   >= H.Hora_Inicio
          AND @Hora_cita   <  H.Hora_Fin
    )
        SET @Disponible = 1;

    RETURN @Disponible;
END;
GO

-- ============================================================
-- Procedimiento: Agendar cita
-- ============================================================
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

    IF @FechaHora <= @Ahora
    BEGIN
        RAISERROR('No se pueden agendar citas en una fecha y hora pasada.', 16, 1);
        RETURN;
    END

    IF DATEDIFF(HOUR, @Ahora, @FechaHora) < 48
    BEGIN
        RAISERROR('La cita debe agendarse con al menos 48 horas de anticipación.', 16, 2);
        RETURN;
    END

    IF @FechaHora > DATEADD(MONTH, 3, @Ahora)
    BEGIN
        RAISERROR('No se pueden agendar citas con más de 3 meses de anticipación.', 16, 3);
        RETURN;
    END

    IF NOT EXISTS (SELECT 1 FROM PACIENTE WHERE Id_paciente = @Id_paciente)
    BEGIN
        RAISERROR('El paciente no existe.', 16, 4);
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

    IF dbo.fn_DoctorDisponible(@Id_doctor, @Fecha_cita, @Hora_cita) = 0
    BEGIN
        RAISERROR('La cita está fuera del horario o día de atención del doctor.', 16, 7);
        RETURN;
    END

    IF EXISTS (
        SELECT 1 FROM CITA
        WHERE Id_doctor  = @Id_doctor
          AND Fecha_cita = @Fecha_cita
          AND hora_cita  = @Hora_cita
          AND Estatus    = 1
    )
    BEGIN
        RAISERROR('El doctor ya tiene una cita en esa fecha y hora.', 16, 8);
        RETURN;
    END

    -- Cita valida (Removidos Diagnostico y Tratamiento, pertenecen a RECETA)
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
-- VISTAS DEL SISTEMA
-- ============================================================

-- Detalle de Citas del Paciente
CREATE OR ALTER VIEW VW_Detalle_Cita_Paciente
AS
SELECT
    C.Id_cita,
    P.Nombre + ' ' + P.Apellido_Paterno + ' ' + ISNULL(P.Apellido_Materno, '') AS Paciente,
    C.Fecha_cita,
    C.hora_cita,
    C.Dia,
    C.Mes,
    C.Estatus,
    E.Nombre + ' ' + E.Apellido_Paterno AS Doctor,
    ES.Nombre AS Especialidad,
    CO.Numero AS Consultorio,
    CO.Piso
FROM CITA C
INNER JOIN PACIENTE P ON C.Id_paciente = P.Id_paciente
INNER JOIN DOCTOR D ON C.Id_doctor = D.Id_doctor
INNER JOIN EMPLEADO E ON D.Id_empleado = E.Id_empleado
INNER JOIN ESPECIALIDAD ES ON D.Id_especialidad = ES.Id_especialidad
INNER JOIN CONSULTORIO CO ON C.Id_consultorio = CO.Id_consultorio;
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