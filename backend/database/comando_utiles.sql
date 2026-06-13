USE CentroMedicoRASA;

SELECT * FROM usuario;

SELECT * FROM EMPLEADO;

SELECT * FROM HORARIO;

SELECT * FROM DOCTOR ORDER BY Id_doctor DESC;

SELECT Id_usuario FROM EMPLEADO;

-- Ver doctores (para saber Id_doctor reales)
SELECT d.Id_doctor, d.Id_empleado, e.Nombre, e.Apellido_Paterno, d.Id_especialidad
FROM DOCTOR d
JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado;

SELECT * FROM ESPECIALIDAD;

SELECT * FROM CITA
