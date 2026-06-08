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