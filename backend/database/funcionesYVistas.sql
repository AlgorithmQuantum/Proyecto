--Edad de Paciente

CREATE FUNCTION FN_EdadPaciente
(
    @IdPaciente INT
)
RETURNS INT
AS
BEGIN

    DECLARE @Edad INT

    SELECT @Edad = Edad
    FROM HISTORIA_MEDICO
    WHERE Id_paciente = @IdPaciente

    RETURN @Edad

END

--Total de Servicios de una Cita
CREATE FUNCTION FN_TotalServicios
(
    @IdCita INT
)
RETURNS FLOAT
AS
BEGIN

    DECLARE @Total FLOAT

    SELECT @Total = SUM(Subtotal)
    FROM CITA_SERVICIO
    WHERE Id_cita = @IdCita

    RETURN ISNULL(@Total,0)

END

--Existencias de Medicamento

CREATE FUNCTION FN_ExistenciasMedicamento
(
    @IdMedicamento INT
)
RETURNS INT
AS
BEGIN

    DECLARE @Existencias INT

    SELECT @Existencias = Existencias
    FROM ALMACEN
    WHERE Id_medicamento = @IdMedicamento

    RETURN @Existencias

END

--Cantidad de Citas por Doctor
CREATE FUNCTION FN_CitasDoctor
(
    @IdDoctor INT
)
RETURNS INT
AS
BEGIN

    DECLARE @Total INT

    SELECT @Total = COUNT(*)
    FROM CITA
    WHERE Id_doctor = @IdDoctor

    RETURN @Total

END

--Detalle de Citas del Paciente
CREATE VIEW VW_Detalle_Cita_Paciente
AS
SELECT
    C.Id_cita,
    P.Nombre + ' ' + P.Apellido_Paterno + ' ' + P.Apellido_Materno AS Paciente,
    C.Fecha_cita,
    C.hora_cita,
    C.Dia,
    C.Mes,
    C.Estatus,
    E.Nombre AS Doctor,
    ES.Nombre AS Especialidad,
    CO.Numero AS Consultorio,
    CO.Piso
FROM CITA C
INNER JOIN PACIENTE P
    ON C.Id_paciente = P.Id_paciente
INNER JOIN DOCTOR D
    ON C.Id_doctor = D.Id_doctor
INNER JOIN EMPLEADO E
    ON D.Id_empleado = E.Id_empleado
INNER JOIN ESPECIALIDAD ES
    ON D.Id_especialidad = ES.Id_especialidad
INNER JOIN CONSULTORIO CO
    ON C.Id_consultorio = CO.Id_consultorio;

    USE CentroMedicoRASA    
    SELECT * FROM cita
    SELECT * FROM VW_Detalle_Cita_Paciente
--Historial Médico del Paciente
CREATE VIEW VW_Historial_Medico
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
INNER JOIN HISTORIA_MEDICO HM
    ON P.Id_paciente = HM.Id_paciente;
       SELECT * FROM VW_Historial_Medico
--Detalle de Pagos
CREATE VIEW VW_Detalle_Pagos
AS
SELECT
    PG.Id_pago,
    PG.Fecha_pago,
    PG.Monto,
    PG.Linea_pago,
    PG.Estatus,
    C.Id_cita,
    P.Nombre + ' ' + P.Apellido_Paterno AS Paciente,
    E.Nombre AS Doctor
FROM PAGO PG
INNER JOIN CITA C
    ON PG.Id_cita = C.Id_cita
INNER JOIN PACIENTE P
    ON C.Id_paciente = P.Id_paciente
INNER JOIN DOCTOR D
    ON C.Id_doctor = D.Id_doctor
INNER JOIN EMPLEADO E
    ON D.Id_empleado = E.Id_empleado;

--Actividad de Doctores
CREATE VIEW VW_Actividad_Doctor
AS
SELECT
    D.Id_doctor,
    E.Nombre AS Doctor,
    ES.Nombre AS Especialidad,
    COUNT(C.Id_cita) AS Total_Citas
FROM DOCTOR D
INNER JOIN EMPLEADO E
    ON D.Id_empleado = E.Id_empleado
INNER JOIN ESPECIALIDAD ES
    ON D.Id_especialidad = ES.Id_especialidad
LEFT JOIN CITA C
    ON D.Id_doctor = C.Id_doctor
GROUP BY
    D.Id_doctor,
    E.Nombre,
    ES.Nombre;
