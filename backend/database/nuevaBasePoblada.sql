USE CentroMedicoRASA;
GO

-- ============================================================
-- ESPECIALIDAD (Agregado Laboratorio Clínico como ID 11)
-- ============================================================
INSERT INTO ESPECIALIDAD (Nombre, Costo_Consulta, Descripcion) VALUES
('Cardiología',         1500.00, 'Diagnóstico y tratamiento del corazón'),
('Dermatología',        1300.00, 'Atención de piel, cabello y uñas'),
('Ginecología',          800.00, 'Salud del sistema reproductor femenino'),
('Medicina General',     500.00, 'Consulta general y preventiva'),
('Nefrología',           800.00, 'Diagnóstico y tratamiento renal'),
('Nutriología',          500.00, 'Orientación nutricional'),
('Oftalmología',         500.00, 'Diagnóstico y tratamiento ocular'),
('Oncología',           1200.00, 'Diagnóstico y tratamiento del cáncer'),
('Ortopedia',            300.00, 'Atención del sistema músculo-esquelético'),
('Pediatría',            700.00, 'Atención médica para niños y adolescentes'),
('Laboratorio Clínico',  600.00, 'Toma de muestras y análisis clínicos');
GO

-- ============================================================
-- HORARIO (Exclusivo Lunes a Viernes)
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
('13:00:00', '21:00:00', 'Viernes');     -- 10
GO

-- ============================================================
-- USUARIO (10 Pacientes, 44 Doctores, 6 Recepcionistas, 2 Farma, 1 Admin)
-- Total 63 usuarios
-- ============================================================
INSERT INTO USUARIO (usuario, contraseña, Rol, Activo, Ultimo_acceso) VALUES
-- Pacientes (Id_usuario 1 al 10)
('jlopez',    'temp123', 'Paciente', 1, '2025-04-10 08:30:00'),
('mgarciafl', 'temp123', 'Paciente', 1, '2025-04-12 10:00:00'),
('cperezjz',  'temp123', 'Paciente', 1, '2025-04-15 09:00:00'),
('lmartinez', 'temp123', 'Paciente', 1, '2025-04-18 11:00:00'),
('rdiaz',     'temp123', 'Paciente', 1, '2025-04-20 14:00:00'),
('vtorres',   'temp123', 'Paciente', 1, '2025-04-22 16:00:00'),
('tmendoza',  'temp123', 'Paciente', 1, '2025-04-23 09:00:00'),
('hsanchez',  'temp123', 'Paciente', 1, '2025-04-24 10:30:00'),
('dcastillo', 'temp123', 'Paciente', 1, '2025-04-25 11:15:00'),
('vcruz',     'temp123', 'Paciente', 1, '2025-04-26 14:45:00'),

-- Doctores (Id_usuario 11 al 54)
('dr_roberto',  'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_ana',      'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_luis_t',   'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_carmen',   'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_laura',    'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_pedro',    'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_elena',    'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_diego',    'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_patricia', 'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_mariana',  'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_silvia',   'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_blanca',   'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_carlos',   'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_hugo',     'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_rosa',     'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_tomas',    'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_sergio',   'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_ines',     'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_fernando', 'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_alicia',   'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('nut_daniela', 'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('nut_jorge',   'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('nut_monica',  'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('nut_ramon',   'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_miguel',   'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_sara',     'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_omar',     'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_diana',    'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_sofia_t',  'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_andres',   'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_beatriz',  'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_victor',   'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_fer_s',    'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_julio',    'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_teresa',   'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_raul',     'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_mar_c',    'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_javier',   'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('dr_lourdes',  'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('dr_esteban',  'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('lab_ricardo', 'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('lab_irma',    'temp321', 'Doctor', 1, '2025-04-10 07:00:00'),
('lab_oscar',   'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),
('lab_elena',   'temp321', 'Doctor', 1, '2025-04-10 13:00:00'),

-- Recepcionistas (Id_usuario 55 al 60)
('recep_ana',   'sup098', 'Recepcionista', 1, '2025-04-10 07:45:00'),
('recep_luis',  'sup098', 'Recepcionista', 1, '2025-04-10 13:45:00'),
('recep_sofia', 'sup098', 'Recepcionista', 1, '2025-04-11 07:30:00'),
('recep_mario', 'sup098', 'Recepcionista', 1, '2025-04-11 13:30:00'),
('recep_lucia', 'sup098', 'Recepcionista', 1, '2025-04-12 07:30:00'),
('recep_fer',   'sup098', 'Recepcionista', 1, '2025-04-12 13:30:00'),

-- Farmacéuticos (Id_usuario 61 al 62)
('farm_pedro',  'drogas666', 'Farmaceutico', 1, '2025-04-10 08:00:00'),
('farm_maria',  'drogas666', 'Farmaceutico', 1, '2025-04-11 08:00:00'),

-- Administrador (Id_usuario 63)
('admin_rasa',  'admin01', 'Administrador',  1, '2025-04-01 09:00:00');
GO

-- ============================================================
-- EMPLEADO (Asocia Id_usuario a la tabla personal)
-- Total: 53 Empleados
-- ============================================================
INSERT INTO EMPLEADO (Id_usuario, Nombre, Apellido_Paterno, Apellido_Materno, Tipo_empleo, Curp, Correo, Telefono, Fecha_contratacion) VALUES
-- Doctores (Id_empleado 1 al 44)
(11, 'Roberto',      'Sánchez', 'López',  'Doctor', 'SAMR800514HDFXXXXX', 'r.sanchez@centrorasa.mx', '5551000101', '2015-03-01'),
(12, 'Ana',          'Valdez',  'Cruz',   'Doctor', 'VALA850312MDFXXXXX', 'a.valdez@centrorasa.mx',  '5551000102', '2016-07-15'),
(13, 'Luis',         'Torres',  'Ruiz',   'Doctor', 'TOLL821105HDFXXXXX', 'l.torres@centrorasa.mx',  '5551000103', '2014-01-20'),
(14, 'Carmen',       'Ríos',    'Vega',   'Doctor', 'RICC880721MDFXXXXX', 'c.rios@centrorasa.mx',    '5551000104', '2018-09-01'),
(15, 'Laura',        'Gómez',   'Díaz',   'Doctor', 'GOLL900115MDFXXXXX', 'l.gomez@centrorasa.mx',   '5551000105', '2017-05-10'),
(16, 'Pedro',        'Ruiz',    'Peña',   'Doctor', 'RUPP790422HDFXXXXX', 'p.ruiz@centrorasa.mx',    '5551000106', '2020-02-14'),
(17, 'Elena',        'Paz',     'Solís',  'Doctor', 'PAEE840910MDFXXXXX', 'e.paz@centrorasa.mx',     '5551000107', '2013-11-05'),
(18, 'Diego',        'Silva',   'Mora',   'Doctor', 'SIDD811230HDFXXXXX', 'd.silva@centrorasa.mx',   '5551000108', '2022-08-01'),
(19, 'Patricia',     'Luna',    'Castro', 'Doctor', 'LUPP860518MDFXXXXX', 'p.luna@centrorasa.mx',    '5551000109', '2015-04-12'),
(20, 'Mariana',      'Castro',  'Pinal',  'Doctor', 'CAMM890808MDFXXXXX', 'm.castro@centrorasa.mx',  '5551000110', '2016-09-03'),
(21, 'Silvia',       'Pinal',   'Díaz',   'Doctor', 'PISS750228MDFXXXXX', 's.pinal@centrorasa.mx',   '5551000111', '2014-02-18'),
(22, 'Blanca',       'Díaz',    'Rivera', 'Doctor', 'DIBB830614MDFXXXXX', 'b.diaz@centrorasa.mx',    '5551000112', '2018-11-20'),
(23, 'Carlos',       'Rivera',  'Montes', 'Doctor', 'RICC801010HDFXXXXX', 'c.rivera@centrorasa.mx',  '5551000113', '2017-07-22'),
(24, 'Hugo',         'Montes',  'Lima',   'Doctor', 'MOHH870404HDFXXXXX', 'h.montes@centrorasa.mx',  '5551000114', '2020-03-15'),
(25, 'Rosa',         'Lima',    'Herrera','Doctor', 'LIRR910909MDFXXXXX', 'r.lima@centrorasa.mx',    '5551000115', '2013-12-10'),
(26, 'Tomás',        'Herrera', 'Peña',   'Doctor', 'HETT820120HDFXXXXX', 't.herrera@centrorasa.mx', '5551000116', '2022-09-05'),
(27, 'Sergio',       'Peña',    'Cruz',   'Doctor', 'PESS851111HDFXXXXX', 's.pena@centrorasa.mx',    '5551000117', '2015-05-14'),
(28, 'Inés',         'Cruz',    'Rey',    'Doctor', 'CRII880303MDFXXXXX', 'i.cruz@centrorasa.mx',    '5551000118', '2016-10-06'),
(29, 'Fernando',     'Rey',     'Cano',   'Doctor', 'REFF790707HDFXXXXX', 'f.rey@centrorasa.mx',     '5551000119', '2014-03-21'),
(30, 'Alicia',       'Cano',    'Solís',  'Doctor', 'CAAA841212MDFXXXXX', 'a.cano@centrorasa.mx',    '5551000120', '2018-12-23'),
(31, 'Daniela',      'Solís',   'Vaca',   'Doctor', 'SODD900505MDFXXXXX', 'd.solis@centrorasa.mx',   '5551000121', '2017-08-25'),
(32, 'Jorge',        'Vaca',    'Gil',    'Doctor', 'VAJJ860806HDFXXXXX', 'j.vaca@centrorasa.mx',    '5551000122', '2020-04-18'),
(33, 'Mónica',       'Gil',     'Ortiz',  'Doctor', 'GIMM890202MDFXXXXX', 'm.gil@centrorasa.mx',     '5551000123', '2013-01-13'),
(34, 'Ramón',        'Ortiz',   'Rey',    'Doctor', 'ORRR831011HDFXXXXX', 'r.ortiz@centrorasa.mx',   '5551000124', '2022-10-08'),
(35, 'Miguel Ángel', 'Rey',     'Pinto',  'Doctor', 'REMM810131HDFXXXXX', 'ma.rey@centrorasa.mx',    '5551000125', '2015-06-17'),
(36, 'Sara',         'Pinto',   'Ríos',   'Doctor', 'PISS920606MDFXXXXX', 's.pinto@centrorasa.mx',   '5551000126', '2016-11-09'),
(37, 'Omar',         'Ríos',    'Mora',   'Doctor', 'RIOO850404HDFXXXXX', 'o.rios@centrorasa.mx',    '5551000127', '2014-04-24'),
(38, 'Diana',        'Mora',    'Torres', 'Doctor', 'MODD870909MDFXXXXX', 'd.mora@centrorasa.mx',    '5551000128', '2018-01-26'),
(39, 'Sofía',        'Torres',  'Vega',   'Doctor', 'TOSS841122MDFXXXXX', 's.torres@centrorasa.mx',  '5551000129', '2017-09-28'),
(40, 'Andrés',       'Vega',    'Sol',    'Doctor', 'VEAA800315HDFXXXXX', 'a.vega@centrorasa.mx',    '5551000130', '2020-05-21'),
(41, 'Beatriz',      'Sol',     'Rivas',  'Doctor', 'SOBB860718MDFXXXXX', 'b.sol@centrorasa.mx',     '5551000131', '2013-02-16'),
(42, 'Víctor',       'Rivas',   'Soto',   'Doctor', 'RIVV821212HDFXXXXX', 'v.rivas@centrorasa.mx',   '5551000132', '2022-11-11'),
(43, 'Fernando',     'Soto',    'Blanco', 'Doctor', 'SOFF790525HDFXXXXX', 'f.soto@centrorasa.mx',    '5551000133', '2015-07-20'),
(44, 'Julio',        'Blanco',  'Cota',   'Doctor', 'BLJJ830808HDFXXXXX', 'j.blanco@centrorasa.mx',  '5551000134', '2016-12-12'),
(45, 'Teresa',       'Cota',    'Parra',  'Doctor', 'COTT880110MDFXXXXX', 't.cota@centrorasa.mx',    '5551000135', '2014-05-27'),
(46, 'Raúl',         'Parra',   'Casos',  'Doctor', 'PARR850420HDFXXXXX', 'r.parra@centrorasa.mx',   '5551000136', '2018-02-28'),
(47, 'Mariana',      'Casos',   'Peña',   'Doctor', 'CAMM910214MDFXXXXX', 'm.casos@centrorasa.mx',   '5551000137', '2017-10-31'),
(48, 'Javier',       'Peña',    'Flores', 'Doctor', 'PEJJ800616HDFXXXXX', 'j.pena@centrorasa.mx',    '5551000138', '2020-06-24'),
(49, 'Lourdes',      'Ruiz',    'Lara',   'Doctor', 'RULL840921MDFXXXXX', 'l.ruiz@centrorasa.mx',    '5551000139', '2013-03-19'),
(50, 'Esteban',      'Flores',  'Meza',   'Doctor', 'FLEE871130HDFXXXXX', 'e.flores@centrorasa.mx',  '5551000140', '2022-12-14'),
(51, 'Ricardo',      'Lara',    'Ruiz',   'Doctor', 'LARR820303HDFXXXXX', 'r.lara@centrorasa.mx',    '5551000141', '2015-08-23'),
(52, 'Irma',         'Ruiz',    'Cruz',   'Doctor', 'RUII890707MDFXXXXX', 'i.ruiz@centrorasa.mx',    '5551000142', '2016-01-15'),
(53, 'Oscar',        'Meza',    'Vaca',   'Doctor', 'MEOO851010HDFXXXXX', 'o.meza@centrorasa.mx',    '5551000143', '2014-06-30'),
(54, 'Elena',        'Cruz',    'Gil',    'Doctor', 'CREE811212MDFXXXXX', 'e.cruz@centrorasa.mx',    '5551000144', '2018-03-02'),

-- Recepcionistas (Id_empleado 55 al 60)
(55, 'Ana',      'Mendoza', 'Vega',    'Recepcionista', 'MEVA920310MDFDNR03', 'a.mendoza@centrorasa.mx', '5551000201', '2021-01-10'),
(56, 'Luis',     'Ortega',  'Paredes', 'Recepcionista', 'ORPL880415HMCTRR04', 'l.ortega@centrorasa.mx',  '5551000202', '2021-06-01'),
(57, 'Sofía',    'Ramos',   'Gómez',   'Recepcionista', 'RAGS950122MDFTRT01', 's.ramos@centrorasa.mx',   '5551000203', '2022-02-15'),
(58, 'Mario',    'Luna',    'Paz',     'Recepcionista', 'LUPM910515HMCTRR05', 'm.luna@centrorasa.mx',    '5551000204', '2022-03-10'),
(59, 'Lucía',    'Ríos',    'Cano',    'Recepcionista', 'RICL980812MDFTRT02', 'l.rios@centrorasa.mx',    '5551000205', '2023-01-20'),
(60, 'Fernando', 'Torres',  'Solís',   'Recepcionista', 'TOSF901130HMCTRR08', 'f.torres@centrorasa.mx',  '5551000206', '2023-05-05'),

-- Farmacéuticos (Id_empleado 61 al 62)
(61, 'Pedro', 'Sánchez', 'Luna', 'Farmaceutico', 'SALP900815HMCNNR07', 'p.sanchez@centrorasa.mx', '5551000301', '2020-05-20'),
(62, 'María', 'Gómez',   'Ruiz', 'Farmaceutico', 'GORM880410MDFNNR03', 'm.gomez@centrorasa.mx',   '5551000302', '2021-08-11'),

-- Administrador (Id_empleado 63)
(63, 'Jorge', 'Ramírez', 'Peña', 'Administrador', 'RAPJ750901HMCMRR02', 'j.ramirez@centrorasa.mx', '5551000401', '2010-01-01');
GO

-- ============================================================
-- DOCTOR (Mapeo de las 11 especialidades, IDs de empleado 1 a 44)
-- ============================================================
INSERT INTO DOCTOR (Id_empleado, Id_especialidad, Id_Horario) VALUES
-- Cardiología (1)
(1, 1, 1), (2, 1, 1), (3, 1, 6), (4, 1, 6),
-- Dermatología (2)
(5, 2, 1), (6, 2, 1), (7, 2, 6), (8, 2, 6),
-- Ginecología (3)
(9, 3, 1), (10, 3, 1), (11, 3, 6), (12, 3, 6),
-- Medicina General (4)
(13, 4, 1), (14, 4, 1), (15, 4, 6), (16, 4, 6),
-- Nefrología (5)
(17, 5, 1), (18, 5, 1), (19, 5, 6), (20, 5, 6),
-- Nutriología (6)
(21, 6, 1), (22, 6, 1), (23, 6, 6), (24, 6, 6),
-- Oftalmología (7)
(25, 7, 1), (26, 7, 1), (27, 7, 6), (28, 7, 6),
-- Oncología (8)
(29, 8, 1), (30, 8, 1), (31, 8, 6), (32, 8, 6),
-- Ortopedia (9)
(33, 9, 1), (34, 9, 1), (35, 9, 6), (36, 9, 6),
-- Pediatría (10)
(37, 10, 1), (38, 10, 1), (39, 10, 6), (40, 10, 6),
-- Laboratorio Clínico (11)
(41, 11, 1), (42, 11, 1), (43, 11, 6), (44, 11, 6);
GO

-- ============================================================
-- EMPLEADO_HORARIO  (Semana completa obligatoria)
-- ============================================================
INSERT INTO EMPLEADO_HORARIO (Id_empleado, Id_Horario) VALUES
-- Matutinos (L-V) para Empleados Impares/Bloque 1
(1,1),(1,2),(1,3),(1,4),(1,5), (2,1),(2,2),(2,3),(2,4),(2,5),
(5,1),(5,2),(5,3),(5,4),(5,5), (6,1),(6,2),(6,3),(6,4),(6,5),
(9,1),(9,2),(9,3),(9,4),(9,5), (10,1),(10,2),(10,3),(10,4),(10,5),
(13,1),(13,2),(13,3),(13,4),(13,5), (14,1),(14,2),(14,3),(14,4),(14,5),
(17,1),(17,2),(17,3),(17,4),(17,5), (18,1),(18,2),(18,3),(18,4),(18,5),
(21,1),(21,2),(21,3),(21,4),(21,5), (22,1),(22,2),(22,3),(22,4),(22,5),
(25,1),(25,2),(25,3),(25,4),(25,5), (26,1),(26,2),(26,3),(26,4),(26,5),
(29,1),(29,2),(29,3),(29,4),(29,5), (30,1),(30,2),(30,3),(30,4),(30,5),
(33,1),(33,2),(33,3),(33,4),(33,5), (34,1),(34,2),(34,3),(34,4),(34,5),
(37,1),(37,2),(37,3),(37,4),(37,5), (38,1),(38,2),(38,3),(38,4),(38,5),
(41,1),(41,2),(41,3),(41,4),(41,5), (42,1),(42,2),(42,3),(42,4),(42,5),

-- Vespertinos (L-V) para Empleados Pares/Bloque 2
(3,6),(3,7),(3,8),(3,9),(3,10), (4,6),(4,7),(4,8),(4,9),(4,10),
(7,6),(7,7),(7,8),(7,9),(7,10), (8,6),(8,7),(8,8),(8,9),(8,10),
(11,6),(11,7),(11,8),(11,9),(11,10), (12,6),(12,7),(12,8),(12,9),(12,10),
(15,6),(15,7),(15,8),(15,9),(15,10), (16,6),(16,7),(16,8),(16,9),(16,10),
(19,6),(19,7),(19,8),(19,9),(19,10), (20,6),(20,7),(20,8),(20,9),(20,10),
(23,6),(23,7),(23,8),(23,9),(23,10), (24,6),(24,7),(24,8),(24,9),(24,10),
(27,6),(27,7),(27,8),(27,9),(27,10), (28,6),(28,7),(28,8),(28,9),(28,10),
(31,6),(31,7),(31,8),(31,9),(31,10), (32,6),(32,7),(32,8),(32,9),(32,10),
(35,6),(35,7),(35,8),(35,9),(35,10), (36,6),(36,7),(36,8),(36,9),(36,10),
(39,6),(39,7),(39,8),(39,9),(39,10), (40,6),(40,7),(40,8),(40,9),(40,10),
(43,6),(43,7),(43,8),(43,9),(43,10), (44,6),(44,7),(44,8),(44,9),(44,10),

-- Horarios Recepcionistas (IDs reales 45 a 50)
(45,1),(45,2),(45,3),(45,4),(45,5),
(46,6),(46,7),(46,8),(46,9),(46,10),
(47,1),(47,2),(47,3),(47,4),(47,5),
(48,6),(48,7),(48,8),(48,9),(48,10),
(49,1),(49,2),(49,3),(49,4),(49,5),
(50,6),(50,7),(50,8),(50,9),(50,10),

-- Horarios Farmacéuticos (IDs reales 51 a 52)
(51,1),(51,2),(51,3),(51,4),(51,5),
(52,6),(52,7),(52,8),(52,9),(52,10),

-- Horario Admin (ID real 53)
(53,1),(53,2),(53,3),(53,4),(53,5);
GO

-- ============================================================
-- RECEPCIONISTA (Usando Id_empleado real 45 a 50)
-- ============================================================
INSERT INTO RECEPCIONISTA (Id_empleado, Hora_Inicio, Hora_Fin) VALUES
(45, '07:00:00', '15:00:00'),
(46, '13:00:00', '21:00:00'),
(47, '07:00:00', '15:00:00'),
(48, '13:00:00', '21:00:00'),
(49, '07:00:00', '15:00:00'),
(50, '13:00:00', '21:00:00');
GO

-- ============================================================
-- CONSULTORIO  (Mapeo real y convertido a números enteros)
-- ============================================================
INSERT INTO CONSULTORIO (Id_Doctor, Numero, Piso, Descripcion) VALUES
(1,  101,   1, 'Cardiología - Sánchez'), (2,  102,   1, 'Cardiología - Valdez'),
(3,  103,   1, 'Cardiología - Torres'),  (4,  104,   1, 'Cardiología - Ríos'),
(5,  201,   2, 'Dermatología - Gómez'),  (6,  202,   2, 'Dermatología - Ruiz'),
(7,  203,   2, 'Dermatología - Paz'),    (8,  204,   2, 'Dermatología - Silva'),
(9,  301,   3, 'Ginecología - Luna'),    (10, 302,   3, 'Ginecología - Castro'),
(11, 303,   3, 'Ginecología - Pinal'),   (12, 304,   3, 'Ginecología - Díaz'),
(13, 901,   0, 'MedGen - Rivera'),       (14, 902,   0, 'MedGen - Montes'),
(15, 903,   0, 'MedGen - Lima'),         (16, 904,   0, 'MedGen - Herrera'),
(17, 401,   4, 'Nefrología - Peña'),     (18, 402,   4, 'Nefrología - Cruz'),
(19, 403,   4, 'Nefrología - Rey'),      (20, 404,   4, 'Nefrología - Cano'),
(21, 501,   5, 'Nutriología - Solís'),   (22, 502,   5, 'Nutriología - Vaca'),
(23, 503,   5, 'Nutriología - Gil'),     (24, 504,   5, 'Nutriología - Ortiz'),
(25, 601,   6, 'Oftalmología - Rey'),    (26, 602,   6, 'Oftalmología - Pinto'),
(27, 603,   6, 'Oftalmología - Ríos'),   (28, 604,   6, 'Oftalmología - Mora'),
(29, 701,   7, 'Oncología - Torres'),    (30, 702,   7, 'Oncología - Vega'),
(31, 703,   7, 'Oncología - Sol'),       (32, 704,   7, 'Oncología - Rivas'),
(33, 801,   8, 'Ortopedia - Soto'),      (34, 802,   8, 'Ortopedia - Blanco'),
(35, 803,   8, 'Ortopedia - Cota'),      (36, 804,   8, 'Ortopedia - Parra'),
(37, 211,   2, 'Pediatría - Casos'),     (38, 212,   2, 'Pediatría - Peña'),
(39, 213,   2, 'Pediatría - Ruiz'),      (40, 214,   2, 'Pediatría - Flores'),
(41, 991,   0, 'Laboratorio - Lara'),    (42, 992,   0, 'Laboratorio - Ruiz'),
(43, 993,   0, 'Laboratorio - Meza'),    (44, 994,   0, 'Laboratorio - Cruz');
GO

-- ============================================================
-- PACIENTE  (IDs corregidos secuenciales del 1 al 10)
-- ============================================================
INSERT INTO PACIENTE (Id_usuario, Nombre, Apellido_Paterno, Apellido_Materno, Curp, Telefono, Correo, Fecha_nacimiento, Edad, Estatura, Peso, Tipo_sangre, Alergias) VALUES
(1,  'Juan',    'López',    'García',  'LOGJ900415HMCPGR03', '5559001001', 'juan.lopez@email.com',    '1990-04-15', 35, 1.75, 78.00, 'O+',  'Ninguna'),
(2,  'María',   'García',   'Flores',  'GAFM950820MDFRRL08', '5559001002', 'maria.garcia@email.com',  '1995-08-20', 29, 1.62, 58.50, 'A+',  'Penicilina'),
(3,  'Carlos',  'Pérez',    'Juárez',  'PEJC880110HMCRRC04', '5559001003', 'carlos.perez@email.com',  '1988-01-10', 37, 1.80, 90.00, 'B+',  'Aspirina'),
(4,  'Laura',   'Martínez', 'Herrera', 'MAHL010305MDFRRR07', '5559001004', 'laura.martinez@email.com','2001-03-05', 24, 1.68, 62.00, 'AB-', 'Sulfonamidas'),
(5,  'Roberto', 'Díaz',     'Salinas', 'DISR750630HMCZLR02', '5559001005', 'roberto.diaz@email.com',  '1975-06-30', 49, 1.72, 85.00, 'A-',  'Ninguna'),
(6,  'Valeria', 'Torres',   'Núñez',   'TONV030912MDFRRR01', '5559001006', 'valeria.torres@email.com','2003-09-12', 21, 1.60, 55.00, 'O-',  'Ibuprofeno'),
(7,  'Teresa',  'Mendoza',  'López',   'MELT850720MDFTRL04', '5559001007', 'teresa.mendoza@email.com','1985-07-20', 40, 1.65, 60.00, 'A+',  'Ninguna'),
(8,  'Hugo',    'Sánchez',  'Márquez', 'SAMH831022HMCTRM09', '5559001008', 'hugo.sanchez@email.com',  '1983-10-22', 42, 1.78, 82.00, 'O+',  'Polen'),
(9,  'Diana',   'Castillo', 'Blanco',  'CABD981215MDFTRB02', '5559001009', 'diana.castillo@email.com','1998-12-15', 27, 1.60, 56.00, 'B-',  'Ninguna'),
(10, 'Víctor',  'Cruz',     'Mora',    'CRMV900218HMCTRM05', '5559001010', 'victor.cruz@email.com',   '1990-02-18', 36, 1.82, 88.00, 'AB+', 'Nueces');
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
(1,  200, 'Tabletas'), (2,  150, 'Cápsulas'), (3,  180, 'Tabletas'),
(4,  120, 'Tabletas'), (5,  160, 'Cápsulas'), (6,  175, 'Tabletas'),
(7,  100, 'Tabletas'), (8,   80, 'Inhalador'), (9,  110, 'Tabletas'),
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
INSERT INTO CITA (Id_paciente, Id_doctor, Id_consultorio, Id_receta, Fecha_cita, hora_cita, Dia, Mes, Estatus, Hora_Fin) VALUES
(1, 1,  1,  1, '2025-03-10', '09:00:00', 10, 3, 1, '09:30:00'),
(2, 5,  5,  2, '2025-03-12', '08:00:00', 12, 3, 1, '08:30:00'),
(3, 13, 13, 3, '2025-03-15', '09:00:00', 15, 3, 1, '09:30:00'),
(4, 9,  9,  4, '2025-03-18', '08:30:00', 18, 3, 1, '09:00:00'),
(5, 1,  1,  5, '2025-03-20', '10:00:00', 20, 3, 1, '10:30:00'),
(6, 13, 13, 6, '2025-03-22', '11:00:00', 22, 3, 1, '11:30:00'),
(1, 5,  5,  NULL, '2025-03-05', '08:00:00', 5,  3, 0, NULL),
(3, 9,  9,  NULL, '2025-03-08', '09:00:00', 8,  3, 0, NULL),
(2, 2,  2,  NULL, DATEADD(DAY, 5,  GETDATE()), '09:00:00', DAY(DATEADD(DAY,5, GETDATE())),  MONTH(DATEADD(DAY,5, GETDATE())),  1, NULL),
(4, 6,  6,  NULL, DATEADD(DAY, 7,  GETDATE()), '14:00:00', DAY(DATEADD(DAY,7, GETDATE())),  MONTH(DATEADD(DAY,7, GETDATE())),  1, NULL),
(5, 3,  3,  NULL, DATEADD(DAY, 10, GETDATE()), '10:00:00', DAY(DATEADD(DAY,10,GETDATE())),  MONTH(DATEADD(DAY,10,GETDATE())), 1, NULL),
(6, 7,  7,  NULL, DATEADD(DAY, 14, GETDATE()), '08:00:00', DAY(DATEADD(DAY,14,GETDATE())),  MONTH(DATEADD(DAY,14,GETDATE())), 1, NULL);
GO

-- ============================================================
-- CITA_SERVICIO
-- ============================================================
INSERT INTO CITA_SERVICIO (Id_cita, Id_servicio, Cantidad, Subtotal) VALUES
(1, 5, 1,  350.00), (1, 9, 1,   80.00), (2, 4, 1,  280.00),
(3, 9, 1,   80.00), (4, 7, 1,  600.00), (5, 5, 1,  350.00),
(5, 4, 1,  280.00), (6, 3, 1,  120.00);
GO

-- ============================================================
-- TICKET
-- ============================================================
INSERT INTO TICKET (Id_cita, Fecha, Subtotal, Monto_total, Estatus_pago) VALUES
(1, '2025-03-10', 1930.00, 1930.00, 'Pagado'),
(2, '2025-03-12', 1860.00, 1860.00, 'Pagado'),
(3, '2025-03-15',  660.00,  660.00, 'Pagado'),
(4, '2025-03-18', 1400.00, 1400.00, 'Pagado'),
(5, '2025-03-20', 2130.00, 2130.00, 'Pagado'),
(6, '2025-03-22',  620.00,  620.00, 'Pagado'),
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
(9,  7, 1300.00, CAST(GETDATE() AS DATE), 0, 'Línea de pago pendiente'),
(10, 8,  800.00, CAST(GETDATE() AS DATE), 0, 'Línea de pago pendiente'),
(11, 9, 1500.00, CAST(GETDATE() AS DATE), 0, 'Línea de pago pendiente'),
(12,10, 1300.00, CAST(GETDATE() AS DATE), 0, 'Línea de pago pendiente');
GO

-- ============================================================
-- BITACORA_CITA
-- ============================================================
INSERT INTO BITACORA_CITA (Id_cita, Id_Recepcionista, Estatus_cita, Monto_devuelto, Inicio, Fin) VALUES
(1, 1, 1,    0.00, '09:00:00', '09:30:00'),
(2, 1, 1,    0.00, '08:00:00', '08:30:00'),
(3, 2, 1,    0.00, '09:00:00', '09:30:00'),
(4, 2, 1,    0.00, '08:30:00', '09:00:00'),
(5, 1, 1,    0.00, '10:00:00', '10:30:00'),
(6, 2, 1,    0.00, '11:00:00', '11:30:00'),
(7, 1, 0, 1500.00, '08:00:00', '08:05:00'),
(8, 2, 0,  250.00, '09:00:00', '09:05:00');
GO

-- ============================================================
-- FARMACEUTICO (Usando Id_empleado 61)
-- ============================================================
INSERT INTO FARMACEUTICO (Id_Empleado, Id_receta_medicina, Id_almacen) VALUES
(61, 1, 4), (61, 2, 10), (61, 3, 5),
(61, 4, 3), (61, 5, 1),  (61, 6, 2);
GO

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
PRINT 'Seed completado exitosamente para CentroMedicoRASA.';
GO