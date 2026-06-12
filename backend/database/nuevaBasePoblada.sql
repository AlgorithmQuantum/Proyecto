-- ============================================================
-- SCRIPT DE POBLACIÓN: CentroMedicoRASA (Completo y Actualizado)
-- ============================================================

-- ============================================================
-- PRIMERA PARTE: Consultorios y Doctores Generales
-- ============================================================
INSERT INTO Consultorios (numero, ubicacion) VALUES 
('101', 'Ala Norte - Piso 1'), ('102', 'Ala Norte - Piso 1'), ('103', 'Ala Norte - Piso 1'), ('104', 'Ala Norte - Piso 1'),
('201', 'Ala Sur - Piso 2'), ('202', 'Ala Sur - Piso 2'), ('203', 'Ala Sur - Piso 2'), ('204', 'Ala Sur - Piso 2'),
('301', 'Ala Este - Piso 3'), ('302', 'Ala Este - Piso 3'), ('303', 'Ala Este - Piso 3'), ('304', 'Ala Este - Piso 3'),
('PB-1', 'Planta Baja - Central'), ('PB-2', 'Planta Baja - Central'), ('PB-3', 'Planta Baja - Central'), ('PB-4', 'Planta Baja - Central'),
('401', 'Ala Oeste - Piso 4'), ('402', 'Ala Oeste - Piso 4'), ('403', 'Ala Oeste - Piso 4'), ('404', 'Ala Oeste - Piso 4'),
('501', 'Ala Norte - Piso 5'), ('502', 'Ala Norte - Piso 5'), ('503', 'Ala Norte - Piso 5'), ('504', 'Ala Norte - Piso 5'),
('601', 'Ala Sur - Piso 6'), ('602', 'Ala Sur - Piso 6'), ('603', 'Ala Sur - Piso 6'), ('604', 'Ala Sur - Piso 6'),
('701', 'Ala Especial - Piso 7'), ('702', 'Ala Especial - Piso 7'), ('703', 'Ala Especial - Piso 7'), ('704', 'Ala Especial - Piso 7'),
('801', 'Ala Este - Piso 8'), ('802', 'Ala Este - Piso 8'), ('803', 'Ala Este - Piso 8'), ('804', 'Ala Este - Piso 8'),
('P-01', 'Ala Infantil - Piso 2'), ('P-02', 'Ala Infantil - Piso 2'), ('P-03', 'Ala Infantil - Piso 2'), ('P-04', 'Ala Infantil - Piso 2'),
('EXT-A', 'Sótano - Laboratorio Clínico'), ('EXT-B', 'Sótano - Laboratorio Clínico'), ('EXT-C', 'Sótano - Laboratorio Clínico'), ('EXT-D', 'Sótano - Laboratorio Clínico');

INSERT INTO Doctores (numero_empleado, nombre, apellidos, curp, fecha_nacimiento, especialidad, cedula_general, id_consultorio, turno, horario_texto) VALUES 
('MED-092', 'Roberto', 'Sánchez López', 'SAMR800514HDFXXXXX', '1980-05-14', 'Cardiología', '8892314', 1, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-093', 'Ana', 'Valdez Cruz', 'VALA850312MDFXXXXX', '1985-03-12', 'Cardiología', '9023412', 2, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-094', 'Luis', 'Torres Ruiz', 'TOLL821105HDFXXXXX', '1982-11-05', 'Cardiología', '7845123', 3, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-095', 'Carmen', 'Ríos Vega', 'RICC880721MDFXXXXX', '1988-07-21', 'Cardiología', '9123847', 4, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-096', 'Laura', 'Gómez Díaz', 'GOLL900115MDFXXXXX', '1990-01-15', 'Dermatología', '9834512', 5, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-097', 'Pedro', 'Ruiz Peña', 'RUPP790422HDFXXXXX', '1979-04-22', 'Dermatología', '6723410', 6, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-098', 'Elena', 'Paz Solís', 'PAEE840910MDFXXXXX', '1984-09-10', 'Dermatología', '8345129', 7, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-099', 'Diego', 'Silva Mora', 'SIDD811230HDFXXXXX', '1981-12-30', 'Dermatología', '7451293', 8, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-100', 'Patricia', 'Luna Castro', 'LUPP860518MDFXXXXX', '1986-05-18', 'Ginecología', '8512394', 9, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-101', 'Mariana', 'Castro Pinal', 'CAMM890808MDFXXXXX', '1989-08-08', 'Ginecología', '9623415', 10, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-102', 'Silvia', 'Pinal Díaz', 'PISS750228MDFXXXXX', '1975-02-28', 'Ginecología', '5612390', 11, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-103', 'Blanca', 'Díaz Rivera', 'DIBB830614MDFXXXXX', '1983-06-14', 'Ginecología', '8234156', 12, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-104', 'Carlos', 'Rivera Montes', 'RICC801010HDFXXXXX', '1980-10-10', 'Medicina General', '7912345', 13, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-105', 'Hugo', 'Montes Lima', 'MOHH870404HDFXXXXX', '1987-04-04', 'Medicina General', '8912346', 14, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-106', 'Rosa', 'Lima Herrera', 'LIRR910909MDFXXXXX', '1991-09-09', 'Medicina General', '9812347', 15, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-107', 'Tomás', 'Herrera Peña', 'HETT820120HDFXXXXX', '1982-01-20', 'Medicina General', '8012348', 16, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-108', 'Sergio', 'Peña Cruz', 'PESS851111HDFXXXXX', '1985-11-11', 'Nefrología', '8512349', 17, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-109', 'Inés', 'Cruz Rey', 'CRII880303MDFXXXXX', '1988-03-03', 'Nefrología', '9112350', 18, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-110', 'Fernando', 'Rey Cano', 'REFF790707HDFXXXXX', '1979-07-07', 'Nefrología', '7612351', 19, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-111', 'Alicia', 'Cano Solís', 'CAAA841212MDFXXXXX', '1984-12-12', 'Nefrología', '8312352', 20, 'Vespertino', '01:00 PM - 09:00 PM'),
('NUT-001', 'Daniela', 'Solís Vaca', 'SODD900505MDFXXXXX', '1990-05-05', 'Nutriología', '9712353', 21, 'Matutino', '07:00 AM - 03:00 PM'),
('NUT-002', 'Jorge', 'Vaca Gil', 'VAJJ860806HDFXXXXX', '1986-08-06', 'Nutriología', '8812354', 22, 'Matutino', '07:00 AM - 03:00 PM'),
('NUT-003', 'Mónica', 'Gil Ortiz', 'GIMM890202MDFXXXXX', '1989-02-02', 'Nutriología', '9512355', 23, 'Vespertino', '01:00 PM - 09:00 PM'),
('NUT-004', 'Ramón', 'Ortiz Rey', 'ORRR831011HDFXXXXX', '1983-10-11', 'Nutriología', '8212356', 24, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-112', 'Miguel Ángel', 'Rey Pinto', 'REMM810131HDFXXXXX', '1981-01-31', 'Oftalmología', '7912357', 25, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-113', 'Sara', 'Pinto Ríos', 'PISS920606MDFXXXXX', '1992-06-06', 'Oftalmología', '9912358', 26, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-114', 'Omar', 'Ríos Mora', 'RIOO850404HDFXXXXX', '1985-04-04', 'Oftalmología', '8412359', 27, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-115', 'Diana', 'Mora Torres', 'MODD870909MDFXXXXX', '1987-09-09', 'Oftalmología', '8912360', 28, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-116', 'Sofía', 'Torres Vega', 'TOSS841122MDFXXXXX', '1984-11-22', 'Oncología', '8312361', 29, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-117', 'Andrés', 'Vega Sol', 'VEAA800315HDFXXXXX', '1980-03-15', 'Oncología', '7812362', 30, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-118', 'Beatriz', 'Sol Rivas', 'SOBB860718MDFXXXXX', '1986-07-18', 'Oncología', '8712363', 31, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-119', 'Víctor', 'Rivas Soto', 'RIVV821212HDFXXXXX', '1982-12-12', 'Oncología', '8112364', 32, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-120', 'Fernando', 'Soto Blanco', 'SOFF790525HDFXXXXX', '1979-05-25', 'Ortopedia', '7612365', 33, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-121', 'Julio', 'Blanco Cota', 'BLJJ830808HDFXXXXX', '1983-08-08', 'Ortopedia', '8212366', 34, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-122', 'Teresa', 'Cota Parra', 'COTT880110MDFXXXXX', '1988-01-10', 'Ortopedia', '9012367', 35, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-123', 'Raúl', 'Parra Casos', 'PARR850420HDFXXXXX', '1985-04-20', 'Ortopedia', '8512368', 36, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-124', 'Mariana', 'Casos Peña', 'CAMM910214MDFXXXXX', '1991-02-14', 'Pediatría', '9812369', 37, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-125', 'Javier', 'Peña Flores', 'PEJJ800616HDFXXXXX', '1980-06-16', 'Pediatría', '7712370', 38, 'Matutino', '07:00 AM - 03:00 PM'),
('MED-126', 'Lourdes', 'Ruiz Lara', 'RULL840921MDFXXXXX', '1984-09-21', 'Pediatría', '8312371', 39, 'Vespertino', '01:00 PM - 09:00 PM'),
('MED-127', 'Esteban', 'Flores Meza', 'FLEE871130HDFXXXXX', '1987-11-30', 'Pediatría', '8912372', 40, 'Vespertino', '01:00 PM - 09:00 PM'),
('LAB-001', 'Ricardo', 'Lara Ruiz', 'LARR820303HDFXXXXX', '1982-03-03', 'Laboratorio Clínico', '8012373', 41, 'Matutino', '07:00 AM - 03:00 PM'),
('LAB-002', 'Irma', 'Ruiz Cruz', 'RUII890707MDFXXXXX', '1989-07-07', 'Laboratorio Clínico', '9512374', 42, 'Matutino', '07:00 AM - 03:00 PM'),
('LAB-003', 'Oscar', 'Meza Vaca', 'MEOO851010HDFXXXXX', '1985-10-10', 'Laboratorio Clínico', '8612375', 43, 'Vespertino', '01:00 PM - 09:00 PM'),
('LAB-004', 'Elena', 'Cruz Gil', 'CREE811212MDFXXXXX', '1981-12-12', 'Laboratorio Clínico', '7912376', 44, 'Vespertino', '01:00 PM - 09:00 PM'); 


-- ============================================================
-- SEGUNDA PARTE: Tablas dependientes de CentroMedicoRASA
-- ============================================================

USE CentroMedicoRASA;
GO

-- ============================================================
-- ESPECIALIDAD 
-- ============================================================
INSERT INTO ESPECIALIDAD (Nombre, Costo_Consulta, Descripcion) VALUES
('Cardiología',      1500.00, 'Diagnóstico y tratamiento de enfermedades del corazón'),
('Dermatología',     1300.00, 'Atención de enfermedades de la piel, cabello y uñas'),
('Ginecología',       800.00, 'Salud del sistema reproductor femenino'),
('Medicina General',  500.00, 'Consulta general y medicina preventiva'),
('Nefrología',        800.00, 'Diagnóstico y tratamiento de enfermedades renales'),
('Nutriología',       500.00, 'Orientación nutricional y planes alimenticios'),
('Oftalmología',      500.00, 'Diagnóstico y tratamiento de enfermedades oculares'),
('Oncología',        1200.00, 'Diagnóstico y tratamiento del cáncer'),
('Ortopedia',         300.00, 'Atención del sistema músculo-esquelético'),
('Pediatría',         700.00, 'Atención médica para niños y adolescentes');
GO

-- ============================================================
-- HORARIO
-- Turno Matutino  07:00-15:00  (Lunes-Viernes)  IDs 1-5
-- Turno Vespertino 13:00-21:00 (Lunes-Viernes)  IDs 6-10
-- Fin de semana                                 IDs 11-12
-- ============================================================
INSERT INTO HORARIO (Hora_Inicio, Hora_Fin, Dia) VALUES
('07:00:00', '15:00:00', 'Lunes'),       -- 1
('07:00:00', '15:00:00', 'Martes'),      -- 2
('07:00:00', '15:00:00', 'Miércoles'),   -- 3
('07:00:00', '15:00:00', 'Jueves'),      -- 4
('07:00:00', '15:00:00', 'Viernes'),     -- 5
('13:00:00', '21:00:00', 'Lunes'),       -- 6
('13:00:00', '21:00:00', 'Martes'),      -- 7
('13:00:00', '21:00:00', 'Miércoles'),   -- 8
('13:00:00', '21:00:00', 'Jueves'),      -- 9
('13:00:00', '21:00:00', 'Viernes'),     -- 10
('08:00:00', '14:00:00', 'Sábado'),      -- 11
('09:00:00', '13:00:00', 'Domingo');     -- 12
GO

-- ============================================================
-- USUARIO (Total: 10 pacientes, 8 doctores, 6 recepcionistas, 2 farmacéuticos, 1 admin)
-- ============================================================
INSERT INTO USUARIO (usuario, password_hash, Rol, Activo, Ultimo_acceso) VALUES
-- Pacientes (1 al 10)
('jlopez',       'temp123', 'Paciente',       1, '2025-04-10 08:30:00'),  -- 1
('mgarciafl',    'temp123', 'Paciente',       1, '2025-04-12 10:00:00'),  -- 2
('cperezjz',     'temp123', 'Paciente',       1, '2025-04-15 09:00:00'),  -- 3
('lmartinez',    'temp123', 'Paciente',       1, '2025-04-18 11:00:00'),  -- 4
('rdiaz',        'temp123', 'Paciente',       1, '2025-04-20 14:00:00'),  -- 5
('vtorres',      'temp123', 'Paciente',       1, '2025-04-22 16:00:00'),  -- 6
('tmendoza',     'temp123', 'Paciente',       1, '2025-04-23 09:00:00'),  -- 19
('hsanchez',     'temp123', 'Paciente',       1, '2025-04-24 10:30:00'),  -- 20
('dcastillo',    'temp123', 'Paciente',       1, '2025-04-25 11:15:00'),  -- 21
('vcruz',        'temp123', 'Paciente',       1, '2025-04-26 14:45:00'),  -- 22
-- Doctores (Id_usuario 7-14)
('dr_acosta',    'temp321', 'Doctor',         1, '2025-04-10 07:00:00'),  -- 7
('dr_bernal',    'temp321', 'Doctor',         1, '2025-04-10 07:00:00'),  -- 8
('dr_carballo',  'temp321', 'Doctor',         1, '2025-04-10 07:00:00'),  -- 9
('dr_delgado',   'temp321', 'Doctor',         1, '2025-04-10 07:00:00'),  -- 10
('dr_estrada',   'temp321', 'Doctor',         1, '2025-04-10 13:00:00'),  -- 11
('dr_fuentes',   'temp321', 'Doctor',         1, '2025-04-10 13:00:00'),  -- 12
('dr_guerrero',  'temp321', 'Doctor',         1, '2025-04-10 13:00:00'),  -- 13
('dr_herrera',   'temp321', 'Doctor',         1, '2025-04-10 13:00:00'),  -- 14
-- Recepcionistas (Total 6)
('recep_ana',    'sup098', 'Recepcionista',   1, '2025-04-10 07:45:00'),  -- 15
('recep_luis',   'sup098', 'Recepcionista',   1, '2025-04-10 13:45:00'),  -- 16
('recep_sofia',  'sup098', 'Recepcionista',   1, '2025-04-11 07:30:00'),  -- 23
('recep_mario',  'sup098', 'Recepcionista',   1, '2025-04-11 13:30:00'),  -- 24
('recep_lucia',  'sup098', 'Recepcionista',   1, '2025-04-12 07:30:00'),  -- 25
('recep_fer',    'sup098', 'Recepcionista',   1, '2025-04-12 13:30:00'),  -- 26
-- Farmacéuticos (Total 2)
('farm_pedro',   'drogas666', 'Farmaceutico', 1, '2025-04-10 08:00:00'),  -- 17
('farm_maria',   'drogas666', 'Farmaceutico', 1, '2025-04-11 08:00:00'),  -- 27
-- Administrador (Total 1)
('admin_rasa',   'admin01', 'Administrador',  1, '2025-04-01 09:00:00');  -- 18
GO

-- ============================================================
-- EMPLEADO
-- (Ordenado para que los IDs secuenciales coincidan con las tablas dependientes)
-- ============================================================
INSERT INTO EMPLEADO (Id_usuario, Nombre, Apellido_Paterno, Apellido_Materno,
                      Tipo_empleo, Curp, Correo, Telefono, Fecha_contratacion) VALUES
-- Doctores (Id_empleado 1-8)
(7,  'Ricardo',   'Acosta',   'Vega',    'Doctor', 'ACVR800101HMCSTR05', 'r.acosta@centrorasa.mx',   '5551000101', '2015-03-01'),
(8,  'Patricia',  'Bernal',   'Cruz',    'Doctor', 'BECP850205MDFRNR09', 'p.bernal@centrorasa.mx',   '5551000102', '2016-07-15'),
(9,  'Miguel',    'Carballo', 'Ríos',    'Doctor', 'CARM780310HMCBSR03', 'm.carballo@centrorasa.mx', '5551000103', '2014-01-20'),
(10, 'Elena',     'Delgado',  'Mora',    'Doctor', 'DEME900415MDFLRR07', 'e.delgado@centrorasa.mx',  '5551000104', '2018-09-01'),
(11, 'Héctor',    'Estrada',  'Nuño',    'Doctor', 'ESNH820520HMCSRR02', 'h.estrada@centrorasa.mx',  '5551000105', '2017-05-10'),
(12, 'Carmen',    'Fuentes',  'Téllez',  'Doctor', 'FUTC950625MDFNRR06', 'c.fuentes@centrorasa.mx',  '5551000106', '2020-02-14'),
(13, 'Andrés',    'Guerrero', 'Salinas', 'Doctor', 'GUSA760730HMCRLN01', 'a.guerrero@centrorasa.mx', '5551000107', '2013-11-05'),
(14, 'Sofía',     'Herrera',  'Paredes', 'Doctor', 'HEPS010835MDFRRD08', 'sofia.herrera@centrorasa.mx','5551000108','2022-08-01'),
-- Recepcionistas (Id_empleado 9-14)
(15, 'Ana',       'Mendoza',  'Vega',    'Recepcionista', 'MEVA920310MDFDNR03', 'a.mendoza@centrorasa.mx', '5551000201', '2021-01-10'),
(16, 'Luis',      'Ortega',   'Paredes', 'Recepcionista', 'ORPL880415HMCTRR04', 'l.ortega@centrorasa.mx',  '5551000202', '2021-06-01'),
(23, 'Sofía',     'Ramos',    'Gómez',   'Recepcionista', 'RAGS950122MDFTRT01', 's.ramos@centrorasa.mx',   '5551000203', '2022-02-15'),
(24, 'Mario',     'Luna',     'Paz',     'Recepcionista', 'LUPM910515HMCTRR05', 'm.luna@centrorasa.mx',    '5551000204', '2022-03-10'),
(25, 'Lucía',     'Ríos',     'Cano',    'Recepcionista', 'RICL980812MDFTRT02', 'l.rios@centrorasa.mx',    '5551000205', '2023-01-20'),
(26, 'Fernando',  'Torres',   'Solís',   'Recepcionista', 'TOSF901130HMCTRR08', 'f.torres@centrorasa.mx',  '5551000206', '2023-05-05'),
-- Farmacéuticos (Id_empleado 15-16)
(17, 'Pedro',     'Sánchez',  'Luna',    'Farmaceutico',  'SALP900815HMCNNR07', 'p.sanchez@centrorasa.mx', '5551000301', '2020-05-20'),
(27, 'María',     'Gómez',    'Ruiz',    'Farmaceutico',  'GORM880410MDFNNR03', 'm.gomez@centrorasa.mx',   '5551000302', '2021-08-11'),
-- Administrador (Id_empleado 17)
(18, 'Jorge',     'Ramírez',  'Peña',    'Administrador', 'RAPJ750901HMCMRR02', 'j.ramirez@centrorasa.mx', '5551000401', '2010-01-01');
GO

-- ============================================================
-- DOCTOR
-- ============================================================
INSERT INTO DOCTOR (Id_empleado, Id_especialidad, Id_Horario) VALUES
-- Cardiología (esp 1)
(1, 1, 1),   -- Acosta    - Lunes matutino
(2, 1, 2),   -- Bernal    - Martes matutino
(3, 1, 6),   -- Carballo  - Lunes vespertino
(4, 1, 7),   -- Delgado   - Martes vespertino
-- Dermatología (esp 2)
(5, 2, 3),   -- Estrada   - Miércoles matutino
(6, 2, 4),   -- Fuentes   - Jueves matutino
(7, 2, 8),   -- Guerrero  - Miércoles vespertino
(8, 2, 9),   -- Herrera   - Jueves vespertino
-- Ginecología (esp 3)
(2, 3, 5),   -- Bernal    - Viernes matutino
(4, 3, 10),  -- Delgado   - Viernes vespertino
(6, 3, 11),  -- Fuentes   - Sábado
(8, 3, 3),   -- Herrera   - Miércoles matutino
-- Medicina General (esp 4)
(1, 4, 2),   -- Acosta    - Martes matutino
(3, 4, 7),   -- Carballo  - Martes vespertino
(5, 4, 4),   -- Estrada   - Jueves matutino
(7, 4, 9),   -- Guerrero  - Jueves vespertino
-- Nefrología (esp 5)
(2, 5, 1),   -- Bernal    - Lunes matutino
(4, 5, 6),   -- Delgado   - Lunes vespertino
(6, 5, 2),   -- Fuentes   - Martes matutino
(8, 5, 7),   -- Herrera   - Martes vespertino
-- Nutriología (esp 6)
(1, 6, 3),   -- Acosta    - Miércoles matutino
(3, 6, 8),   -- Carballo  - Miércoles vespertino
(5, 6, 5),   -- Estrada   - Viernes matutino
(7, 6, 10),  -- Guerrero  - Viernes vespertino
-- Oftalmología (esp 7)
(2, 7, 4),   -- Bernal    - Jueves matutino
(4, 7, 9),   -- Delgado   - Jueves vespertino
(6, 7, 11),  -- Fuentes   - Sábado
(8, 7, 1),   -- Herrera   - Lunes matutino
-- Oncología (esp 8)
(1, 8, 5),   -- Acosta    - Viernes matutino
(3, 8, 10),  -- Carballo  - Viernes vespertino
(5, 8, 1),   -- Estrada   - Lunes matutino
(7, 8, 6),   -- Guerrero  - Lunes vespertino
-- Ortopedia (esp 9)
(2, 9, 3),   -- Bernal    - Miércoles matutino
(4, 9, 8),   -- Delgado   - Miércoles vespertino
(6, 9, 5),   -- Fuentes   - Viernes matutino
(8, 9, 10),  -- Herrera   - Viernes vespertino
-- Pediatría (esp 10)
(1, 10, 4),  -- Acosta    - Jueves matutino
(3, 10, 9),  -- Carballo  - Jueves vespertino
(5, 10, 2),  -- Estrada   - Martes matutino
(7, 10, 7);  -- Guerrero  - Martes vespertino
GO

-- ============================================================
-- EMPLEADO_HORARIO  (relación auxiliar)
-- ============================================================
INSERT INTO EMPLEADO_HORARIO (Id_empleado, Id_Horario) VALUES
(1, 1),(1, 2),(1, 3),(1, 4),(1, 5),
(2, 1),(2, 2),(2, 3),(2, 4),(2, 5),
(3, 6),(3, 7),(3, 8),(3, 9),(3,10),
(4, 6),(4, 7),(4, 8),(4, 9),(4,10),
(5, 1),(5, 2),(5, 3),(5, 4),(5, 5),
(6, 6),(6, 7),(6, 8),(6, 9),(6,10),
(7, 1),(7, 2),(7, 3),(7, 4),(7, 5),
(8, 6),(8, 7),(8, 8),(8, 9),(8,10),
(9, 1),(9, 2),(9, 3),(9, 4),(9, 5),  -- recepcionista Ana
(10,6),(10,7),(10,8),(10,9),(10,10); -- recepcionista Luis
GO

-- ============================================================
-- RECEPCIONISTA (Usando Id_empleado 9 a 14)
-- ============================================================
INSERT INTO RECEPCIONISTA (Id_empleado, Hora_Inicio, Hora_Fin) VALUES
(9,  '07:00:00', '15:00:00'),  -- Ana
(10, '13:00:00', '21:00:00'),  -- Luis
(11, '07:00:00', '15:00:00'),  -- Sofía
(12, '13:00:00', '21:00:00'),  -- Mario
(13, '07:00:00', '15:00:00'),  -- Lucía
(14, '13:00:00', '21:00:00');  -- Fernando
GO

-- ============================================================
-- CONSULTORIO  (uno por doctor-especialidad activo)
-- ============================================================
INSERT INTO CONSULTORIO (Id_Doctor, Numero, Piso, Descripcion) VALUES
-- Cardiología
(1,  101, 1, 'Cardiología - Acosta'),
(2,  102, 1, 'Cardiología - Bernal'),
(3,  103, 1, 'Cardiología - Carballo'),
(4,  104, 1, 'Cardiología - Delgado'),
-- Dermatología
(5,  201, 2, 'Dermatología - Estrada'),
(6,  202, 2, 'Dermatología - Fuentes'),
(7,  203, 2, 'Dermatología - Guerrero'),
(8,  204, 2, 'Dermatología - Herrera'),
-- Ginecología
(9,  301, 3, 'Ginecología - Bernal'),
(10, 302, 3, 'Ginecología - Delgado'),
(11, 303, 3, 'Ginecología - Fuentes'),
(12, 304, 3, 'Ginecología - Herrera'),
-- Medicina General
(13, 401, 4, 'Medicina General - Acosta'),
(14, 402, 4, 'Medicina General - Carballo'),
(15, 403, 4, 'Medicina General - Estrada'),
(16, 404, 4, 'Medicina General - Guerrero');
GO

-- ============================================================
-- PACIENTE  (Los 10 pacientes)
-- ============================================================
INSERT INTO PACIENTE (Id_usuario, Nombre, Apellido_Paterno, Apellido_Materno,
                      Curp, Telefono, Correo, Fecha_nacimiento, Edad,
                      Estatura, Peso, Tipo_sangre, Alergias) VALUES
(1,  'Juan',    'López',    'García',  'LOGJ900415HMCPGR03', '5559001001', 'juan.lopez@email.com',    '1990-04-15', 35, 1.75, 78.00, 'O+',  'Ninguna'),
(2,  'María',   'García',   'Flores',  'GAFM950820MDFRRL08', '5559001002', 'maria.garcia@email.com',  '1995-08-20', 29, 1.62, 58.50, 'A+',  'Penicilina'),
(3,  'Carlos',  'Pérez',    'Juárez',  'PEJC880110HMCRRC04', '5559001003', 'carlos.perez@email.com',  '1988-01-10', 37, 1.80, 90.00, 'B+',  'Aspirina'),
(4,  'Laura',   'Martínez', 'Herrera', 'MAHL010305MDFRRR07', '5559001004', 'laura.martinez@email.com','2001-03-05', 24, 1.68, 62.00, 'AB-', 'Sulfonamidas'),
(5,  'Roberto', 'Díaz',     'Salinas', 'DISR750630HMCZLR02', '5559001005', 'roberto.diaz@email.com',  '1975-06-30', 49, 1.72, 85.00, 'A-',  'Ninguna'),
(6,  'Valeria', 'Torres',   'Núñez',   'TONV030912MDFRRR01', '5559001006', 'valeria.torres@email.com','2003-09-12', 21, 1.60, 55.00, 'O-',  'Ibuprofeno'),
(19, 'Teresa',  'Mendoza',  'López',   'MELT850720MDFTRL04', '5559001007', 'teresa.mendoza@email.com','1985-07-20', 40, 1.65, 60.00, 'A+',  'Ninguna'),
(20, 'Hugo',    'Sánchez',  'Márquez', 'SAMH831022HMCTRM09', '5559001008', 'hugo.sanchez@email.com',  '1983-10-22', 42, 1.78, 82.00, 'O+',  'Polen'),
(21, 'Diana',   'Castillo', 'Blanco',  'CABD981215MDFTRB02', '5559001009', 'diana.castillo@email.com','1998-12-15', 27, 1.60, 56.00, 'B-',  'Ninguna'),
(22, 'Víctor',  'Cruz',     'Mora',    'CRMV900218HMCTRM05', '5559001010', 'victor.cruz@email.com',   '1990-02-18', 36, 1.82, 88.00, 'AB+', 'Nueces');
GO

-- ============================================================
-- HISTORIA_MEDICO
-- ============================================================
INSERT INTO HISTORIA_MEDICO (Id_paciente, Tipo_sangre, Estatura, Peso, Edad, Alergias) VALUES
(1,  'O+',  1.75, 78.00, 35, 'Ninguna'),
(2,  'A+',  1.62, 58.50, 29, 'Penicilina'),
(3,  'B+',  1.80, 90.00, 37, 'Aspirina'),
(4,  'AB-', 1.68, 62.00, 24, 'Sulfonamidas'),
(5,  'A-',  1.72, 85.00, 49, 'Ninguna'),
(6,  'O-',  1.60, 55.00, 21, 'Ibuprofeno'),
(7,  'A+',  1.65, 60.00, 40, 'Ninguna'),
(8,  'O+',  1.78, 82.00, 42, 'Polen'),
(9,  'B-',  1.60, 56.00, 27, 'Ninguna'),
(10, 'AB+', 1.82, 88.00, 36, 'Nueces');
GO

-- ============================================================
-- MEDICAMENTO
-- ============================================================
INSERT INTO MEDICAMENTO (Nombre, Descripcion, Concentracion, Precio, Stock) VALUES
('Paracetamol',    'Analgésico y antipirético',          '500mg',  12.50, 200),
('Amoxicilina',    'Antibiótico de amplio espectro',     '500mg',  45.00, 150),
('Metformina',     'Antidiabético oral',                 '850mg',  38.00, 180),
('Losartán',       'Antihipertensivo',                   '50mg',   55.00, 120),
('Omeprazol',      'Inhibidor de la bomba de protones',  '20mg',   22.00, 160),
('Ibuprofeno',     'Antiinflamatorio no esteroideo',     '400mg',  18.00, 175),
('Atorvastatina',  'Reductor de colesterol',             '20mg',   65.00, 100),
('Salbutamol',     'Broncodilatador',                    '100mcg', 90.00,  80),
('Ciprofloxacino', 'Antibiótico quinolona',              '500mg',  52.00, 110),
('Diclofenaco',    'Antiinflamatorio tópico/oral',       '50mg',   20.00, 130);
GO

-- ============================================================
-- ALMACEN
-- ============================================================
INSERT INTO ALMACEN (Id_medicamento, Existencias, Tipo) VALUES
(1,  200, 'Tabletas'),
(2,  150, 'Cápsulas'),
(3,  180, 'Tabletas'),
(4,  120, 'Tabletas'),
(5,  160, 'Cápsulas'),
(6,  175, 'Tabletas'),
(7,  100, 'Tabletas'),
(8,   80, 'Inhalador'),
(9,  110, 'Tabletas'),
(10, 130, 'Grageas');
GO

-- ============================================================
-- SERVICIO
-- ============================================================
INSERT INTO SERVICIO (Nombre, Costo, Descripcion) VALUES
('Inyección',             80.00,  'Aplicación de medicamento intramuscular o intravenosa'),
('Vacuna',               150.00,  'Aplicación de vacuna con registro en cartilla'),
('Curación',             120.00,  'Limpieza y vendaje de heridas'),
('Estudio de sangre',    280.00,  'Biometría hemática y química sanguínea'),
('Electrocardiograma',   350.00,  'Estudio eléctrico del corazón'),
('Radiografía de tórax', 400.00,  'Imagen diagnóstica de cavidad torácica'),
('Ultrasonido abdominal',600.00,  'Estudio de órganos abdominales'),
('Espirometría',         300.00,  'Prueba de función pulmonar'),
('Glucometría',           80.00,  'Medición de glucosa en sangre'),
('Presión arterial',      50.00,  'Medición y registro de presión arterial');
GO

-- ============================================================
-- RECETA  (citas ya atendidas — fechas pasadas)
-- ============================================================
INSERT INTO RECETA (Id_paciente, Id_doctor, Fecha, Diagnostico, Tratamiento, Indicaciones) VALUES
(1, 1,  '2025-03-10', 'Hipertensión arterial leve',    'Antihipertensivo diario',       'Dieta baja en sodio, caminar 30 min/día'),
(2, 5,  '2025-03-12', 'Dermatitis atópica',            'Antiinflamatorio tópico',        'Aplicar crema 2 veces/día, evitar sol directo'),
(3, 13, '2025-03-15', 'Gastritis crónica',             'Protector gástrico en ayunas',   'Evitar picante y alcohol'),
(4, 9,  '2025-03-18', 'Control ginecológico anual',    'Sin tratamiento farmacológico',  'Próxima revisión en 12 meses'),
(5, 1,  '2025-03-20', 'Diabetes tipo 2 controlada',   'Antidiabético oral + dieta',     'Monitorear glucosa en ayunas cada 3 días'),
(6, 13, '2025-03-22', 'Faringitis aguda',              'Antibioticoterapia 7 días',      'Reposo, ingesta de líquidos, no suspender AB');
GO

-- ============================================================
-- RECETA_MEDICINA
-- ============================================================
INSERT INTO RECETA_MEDICINA (Id_receta, Id_medicamento, Dosis, Frecuencia, Indicaciones, Cantidad) VALUES
(1, 4,  50.00, 'Una vez al día por la mañana',    'Con o sin alimentos',          30),
(2, 10, 50.00, 'Cada 12 horas por 5 días',        'Con comida, uso tópico',       10),
(3, 5,  20.00, 'Una vez al día en ayunas',        'Antes del desayuno',           30),
(5, 3,  850.00,'Dos veces al día',                'Con el desayuno y la cena',    60),
(5, 1,  500.00,'Si glucosa >180 mg/dL',           'No exceder 3 tomas/día',       12),
(6, 2,  500.00,'Cada 8 horas por 7 días',         'Tomar con alimentos completos',21);
GO

-- ============================================================
-- CITA
-- ============================================================
INSERT INTO CITA (Id_paciente, Id_doctor, Id_consultorio, Id_receta,
                  Fecha_cita, hora_cita, Dia, Mes, Estatus, Hora_Fin) VALUES
-- ── Citas atendidas (historial) ──────────────────────────────
(1, 1,  1,  1, '2025-03-10', '09:00:00', 10, 3, 1, '09:30:00'),  -- Cardio - Juan
(2, 5,  5,  2, '2025-03-12', '08:00:00', 12, 3, 1, '08:30:00'),  -- Dermato - María
(3, 13, 13, 3, '2025-03-15', '09:00:00', 15, 3, 1, '09:30:00'),  -- MedGen - Carlos
(4, 9,  9,  4, '2025-03-18', '08:30:00', 18, 3, 1, '09:00:00'),  -- Gineco - Laura
(5, 1,  1,  5, '2025-03-20', '10:00:00', 20, 3, 1, '10:30:00'),  -- Cardio - Roberto
(6, 13, 13, 6, '2025-03-22', '11:00:00', 22, 3, 1, '11:30:00'),  -- MedGen - Valeria
-- ── Citas canceladas (para poblar bitácora) ───────────────────
(1, 5,  5,  NULL, '2025-03-05', '08:00:00', 5,  3, 0, NULL),     -- Cancelada - Juan
(3, 9,  9,  NULL, '2025-03-08', '09:00:00', 8,  3, 0, NULL),     -- Cancelada - Carlos
-- ── Citas futuras (estado Agendada pendiente de pago) ─────────
-- En producción se crearían vía sp_CrearCita
(2, 2,  2,  NULL, DATEADD(DAY, 5,  GETDATE()), '09:00:00', DAY(DATEADD(DAY,5, GETDATE())),  MONTH(DATEADD(DAY,5, GETDATE())),  1, NULL),
(4, 6,  6,  NULL, DATEADD(DAY, 7,  GETDATE()), '14:00:00', DAY(DATEADD(DAY,7, GETDATE())),  MONTH(DATEADD(DAY,7, GETDATE())),  1, NULL),
(5, 3,  3,  NULL, DATEADD(DAY, 10, GETDATE()), '10:00:00', DAY(DATEADD(DAY,10,GETDATE())),  MONTH(DATEADD(DAY,10,GETDATE())), 1, NULL),
(6, 7,  7,  NULL, DATEADD(DAY, 14, GETDATE()), '08:00:00', DAY(DATEADD(DAY,14,GETDATE())),  MONTH(DATEADD(DAY,14,GETDATE())), 1, NULL);
GO

-- ============================================================
-- CITA_SERVICIO  (servicios asociados a citas atendidas)
-- ============================================================
INSERT INTO CITA_SERVICIO (Id_cita, Id_servicio, Cantidad, Subtotal) VALUES
(1, 5, 1,  350.00),   -- Electrocardiograma en cita cardio Juan
(1, 9, 1,   80.00),   -- Glucometría en cita cardio Juan
(2, 4, 1,  280.00),   -- Estudio de sangre en cita dermato María
(3, 9, 1,   80.00),   -- Glucometría en cita MedGen Carlos
(4, 7, 1,  600.00),   -- Ultrasonido abdominal en cita gineco Laura
(5, 5, 1,  350.00),   -- Electrocardiograma en cita cardio Roberto
(5, 4, 1,  280.00),   -- Estudio de sangre cita cardio Roberto
(6, 3, 1,  120.00);   -- Curación en cita MedGen Valeria
GO

-- ============================================================
-- TICKET  (generado al confirmar pago, 8h después de agendar)
-- ============================================================
INSERT INTO TICKET (Id_cita, Fecha, Subtotal, Monto_total, Estatus_pago) VALUES
(1, '2025-03-10', 1930.00, 1930.00, 'Pagado'),    -- Cardio Juan:  1500+350+80
(2, '2025-03-12', 1860.00, 1860.00, 'Pagado'),    -- Dermato María: 1300+280+150(vacuna anterior) → 1580 aprox
(3, '2025-03-15',  660.00,  660.00, 'Pagado'),    -- MedGen Carlos: 500+80+80
(4, '2025-03-18', 1400.00, 1400.00, 'Pagado'),    -- Gineco Laura: 800+600
(5, '2025-03-20', 2130.00, 2130.00, 'Pagado'),    -- Cardio Roberto: 1500+350+280
(6, '2025-03-22',  620.00,  620.00, 'Pagado'),    -- MedGen Valeria: 500+120
-- Tickets citas futuras - pendientes de pago (8h para confirmar)
(9,  CAST(GETDATE() AS DATE), 1300.00, 1300.00, 'Pendiente'),
(10, CAST(GETDATE() AS DATE),  800.00,  800.00, 'Pendiente'),
(11, CAST(GETDATE() AS DATE), 1500.00, 1500.00, 'Pendiente'),
(12, CAST(GETDATE() AS DATE), 1300.00, 1300.00, 'Pendiente');
GO

-- ============================================================
-- PAGO
-- ============================================================
INSERT INTO PAGO (Id_cita, Id_ticket, Monto, Fecha_pago, Estatus, Linea_pago) VALUES
(1, 1, 1930.00, '2025-03-10', 1, 'Efectivo'),
(2, 2, 1860.00, '2025-03-12', 1, 'Tarjeta de crédito'),
(3, 3,  660.00, '2025-03-15', 1, 'Transferencia SPEI'),
(4, 4, 1400.00, '2025-03-18', 1, 'Tarjeta de débito'),
(5, 5, 2130.00, '2025-03-20', 1, 'Efectivo'),
(6, 6,  620.00, '2025-03-22', 1, 'Transferencia SPEI'),
-- Pagos pendientes de citas futuras
(9,  7, 1300.00, CAST(GETDATE() AS DATE), 0, 'Línea de pago pendiente'),
(10, 8,  800.00, CAST(GETDATE() AS DATE), 0, 'Línea de pago pendiente'),
(11, 9, 1500.00, CAST(GETDATE() AS DATE), 0, 'Línea de pago pendiente'),
(12,10, 1300.00, CAST(GETDATE() AS DATE), 0, 'Línea de pago pendiente');
GO

-- ============================================================
-- BITACORA_CITA
-- ============================================================
INSERT INTO BITACORA_CITA (Id_cita, Id_Recepcionista, Estatus_cita, Monto_devuelto, Inicio, Fin) VALUES
-- Citas atendidas - registro de atención
(1, 1, 1,    0.00, '09:00:00', '09:30:00'),
(2, 1, 1,    0.00, '08:00:00', '08:30:00'),
(3, 2, 1,    0.00, '09:00:00', '09:30:00'),
(4, 2, 1,    0.00, '08:30:00', '09:00:00'),
(5, 1, 1,    0.00, '10:00:00', '10:30:00'),
(6, 2, 1,    0.00, '11:00:00', '11:30:00'),
-- Citas canceladas - política de cancelación
(7, 1, 0, 1500.00, '08:00:00', '08:05:00'),   -- Cancelada >48h: 100% (Cardio $1500)
(8, 2, 0,  250.00, '09:00:00', '09:05:00');   -- Cancelada 24-48h: 50% (Gineco $500)
GO

-- ============================================================
-- FARMACEUTICO (Actualizado para referenciar el nuevo Id_empleado 15)
-- ============================================================
INSERT INTO FARMACEUTICO (Id_Empleado, Id_receta_medicina, Id_almacen) VALUES
(15, 1, 4),   -- Pedro despacha Losartán para receta 1
(15, 2, 10),  -- Pedro despacha Diclofenaco para receta 2
(15, 3, 5),   -- Pedro despacha Omeprazol para receta 3
(15, 4, 3),   -- Pedro despacha Metformina para receta 5
(15, 5, 1),   -- Pedro despacha Paracetamol para receta 5
(15, 6, 2);   -- Pedro despacha Amoxicilina para receta 6
GO

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
PRINT 'Seed completado exitosamente para CentroMedicoRASA.';
GO