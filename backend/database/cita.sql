USE CentroMedicoRASA;
GO

--========================================================
--Funcion: Verifica si la cita es en el horario del doctor.
--========================================================
CREATE FUNCTION fn_DoctorDisponible
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

-- ============================================
-- Procedimiento: Agendar cita
-- ============================================
CREATE PROCEDURE sp_CrearCita
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

    -- Verificar que no sea hora pasada.
    IF @FechaHora <= @Ahora
    BEGIN
        RAISERROR('No se pueden agendar citas en una fecha y hora pasada.', 16, 1);
        RETURN;
    END

    -- Verificar la anticipacion de 48 horas
    IF DATEDIFF(HOUR, @Ahora, @FechaHora) < 48
    BEGIN
        RAISERROR('La cita debe agendarse con al menos 48 horas de anticipación.', 16, 2);
        RETURN;
    END

    -- Verificar que la cita fue hecha con 3 meses de anticipacion
    IF @FechaHora > DATEADD(MONTH, 3, @Ahora)
    BEGIN
        RAISERROR('No se pueden agendar citas con más de 3 meses de anticipación.', 16, 3);
        RETURN;
    END

    -- ============== Validar que el paciente exista ======================
    IF NOT EXISTS (SELECT 1 FROM PACIENTE WHERE Id_paciente = @Id_paciente)
    BEGIN
        RAISERROR('El paciente no existe.', 16, 4);
        RETURN;
    END

    -- ============ Validar que el doctor exista ===================
    IF NOT EXISTS (SELECT 1 FROM DOCTOR WHERE Id_doctor = @Id_doctor)
    BEGIN
        RAISERROR('El doctor no existe.', 16, 5);
        RETURN;
    END

    -- ================= Validar que el consultorio exista =========================
    IF NOT EXISTS (SELECT 1 FROM CONSULTORIO WHERE Id_consultorio = @Id_consultorio)
    BEGIN
        RAISERROR('El consultorio no existe.', 16, 6);
        RETURN;
    END

    -- ========= Cita dentro del horario del doctor ===================
    IF dbo.fn_DoctorDisponible(@Id_doctor, @Fecha_cita, @Hora_cita) = 0
    BEGIN
        RAISERROR('La cita está fuera del horario o día de atención del doctor.', 16, 7);
        RETURN;
    END

    -- ======= Doctor sin traslape en esa fecha/hora ===================
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

    -- Cita valida
    INSERT INTO CITA (
        Id_paciente,
        Id_doctor,
        Id_consultorio,
        Id_receta,
        Fecha_cita,
        hora_cita,
        Dia,
        Mes,
        Estatus,
        Diagnostico,
        Tratamiento,
        Hora_Fin
    )
    VALUES (
        @Id_paciente,
        @Id_doctor,
        @Id_consultorio,
        @Fecha_cita,
        @Hora_cita,
        @Dia,
        @Mes,
        1,
        @Hora_Fin
    );

    PRINT 'Cita agendada exitosamente.';

END;
GO

