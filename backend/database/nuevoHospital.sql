-- ============================================================================
-- 1. CONTROL DE ACCESO Y USUARIOS GLOBALES
-- ============================================================================
CREATE TABLE Usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL CHECK (rol IN ('Administrador', 'Doctor', 'Recepcionista', 'Farmaceutico', 'Paciente')),
    estado BIT DEFAULT 1,
    fecha_creacion DATETIME DEFAULT GETDATE()
);

-- ============================================================================
-- 2. PERSONAL ADMINISTRATIVO (Módulo Recepción)
-- ============================================================================
CREATE TABLE Recepcionistas (
    id_recepcionista INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT UNIQUE,
    nombre_completo VARCHAR(150) NOT NULL,
    turno VARCHAR(50) NOT NULL CHECK (turno IN ('Matutino', 'Vespertino', 'Nocturno', 'Fin de Semana')),
    telefono VARCHAR(20),
    correo VARCHAR(100) UNIQUE NOT NULL,
    fecha_contratacion DATE DEFAULT GETDATE()
);

-- ============================================================================
-- 3. INFRAESTRUCTURA HOSPITALARIA Y PERSONAL MÉDICO
-- ============================================================================
CREATE TABLE Especialidades (
    id_especialidad INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    costo_consulta DECIMAL(10, 2) NOT NULL,
    icono VARCHAR(50) DEFAULT 'fa-notes-medical'
);

CREATE TABLE Consultorios (
    id_consultorio INT IDENTITY(1,1) PRIMARY KEY,
    piso INT NOT NULL,
    numero VARCHAR(20) NOT NULL,
    ala VARCHAR(50) NOT NULL,
    estatus VARCHAR(20) DEFAULT 'Disponible' CHECK (estatus IN ('Disponible', 'Ocupado', 'Mantenimiento')),
    id_doctor_actual INT NULL 
);

CREATE TABLE Doctores (
    id_doctor INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT UNIQUE,
    cedula_profesional VARCHAR(50) UNIQUE NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    id_especialidad INT,
    id_consultorio INT,
    correo VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20)
);

CREATE TABLE Horarios_Doctores (
    id_horario INT IDENTITY(1,1) PRIMARY KEY,
    id_doctor INT,
    dia_semana VARCHAR(20) NOT NULL CHECK (dia_semana IN ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo')),
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
);

-- ============================================================================
-- 4. PACIENTES Y EXPEDIENTE CLÍNICO BASE
-- ============================================================================
CREATE TABLE Pacientes (
    id_paciente INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT UNIQUE,
    curp VARCHAR(18) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),
    fecha_nacimiento DATE NOT NULL,
    genero VARCHAR(20) NOT NULL CHECK (genero IN ('Masculino', 'Femenino', 'Otro')),
    correo VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    direccion TEXT,
    tipo_sangre VARCHAR(5),
    contacto_emergencia_nombre VARCHAR(150),
    contacto_emergencia_telefono VARCHAR(20),
    notif_citas BIT DEFAULT 1,
    compartir_expediente BIT DEFAULT 0,
    fecha_registro DATETIME DEFAULT GETDATE()
);

CREATE TABLE Antecedentes_Medicos (
    id_antecedente INT IDENTITY(1,1) PRIMARY KEY,
    id_paciente INT,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('Alergia', 'Padecimiento Crónico')),
    descripcion VARCHAR(150) NOT NULL
);

-- ============================================================================
-- 5. CONTROL DE CITAS Y CHECK-IN DE RECEPCIÓN
-- ============================================================================
CREATE TABLE Citas (
    id_cita INT IDENTITY(1,1) PRIMARY KEY,
    folio VARCHAR(50) UNIQUE NOT NULL,
    id_paciente INT,
    id_doctor INT,
    id_especialidad INT,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    -- ESTADOS EXACTOS SOLICITADOS EN EL PDF
    estatus VARCHAR(50) DEFAULT 'Agendada pendiente de pago' 
    CHECK (estatus IN (
        'Agendada pendiente de pago', 
        'Pagada pendiente por consulta', 
        'Cancelada por falta de pago', 
        'Atendida', 
        'Cancelada por el paciente', 
        'Cancelada por el doctor', 
        'No asistió'
    )),
    fecha_limite_pago DATETIME NOT NULL, -- Para controlar la regla de prepago de 8 hrs
    motivo_cancelacion TEXT,
    fecha_creacion DATETIME DEFAULT GETDATE()
);

CREATE TABLE Registro_Llegadas (
    id_llegada INT IDENTITY(1,1) PRIMARY KEY,
    id_cita INT UNIQUE,
    id_recepcionista INT,
    hora_llegada DATETIME DEFAULT GETDATE(),
    tiempo_espera_estimado INT
);

CREATE TABLE Consultas_Expediente (
    id_consulta INT IDENTITY(1,1) PRIMARY KEY,
    id_cita INT UNIQUE,
    id_paciente INT,
    peso DECIMAL(5,2),
    altura DECIMAL(3,2),
    temperatura DECIMAL(4,1),
    presion_arterial VARCHAR(20),
    frecuencia_cardiaca INT,
    sintomas TEXT NOT NULL,
    diagnostico TEXT NOT NULL,
    notas_clinicas TEXT,
    fecha_registro DATETIME DEFAULT GETDATE()
);

-- ============================================================================
-- 6. FINANZAS: CAJA, SERVICIOS EXTERNOS Y REEMBOLSOS
-- ============================================================================
CREATE TABLE Cortes_Caja (
    id_corte INT IDENTITY(1,1) PRIMARY KEY,
    id_recepcionista INT,
    fecha_apertura DATETIME DEFAULT GETDATE(),
    fecha_cierre DATETIME NULL,
    monto_inicial DECIMAL(10,2) NOT NULL,
    monto_calculado DECIMAL(10,2) NULL,
    monto_real DECIMAL(10,2) NULL,
    diferencia DECIMAL(10,2) NULL,
    estatus VARCHAR(20) DEFAULT 'Abierta' CHECK (estatus IN ('Abierta', 'Cerrada'))
);

-- Tabla para vender servicios a NO pacientes (Regla del PDF)
CREATE TABLE Ventas_Servicios (
    id_venta_servicio INT IDENTITY(1,1) PRIMARY KEY,
    folio_venta VARCHAR(50) UNIQUE NOT NULL,
    descripcion_servicio VARCHAR(200) NOT NULL,
    id_paciente INT NULL, -- Es NULL si el cliente no está registrado
    id_recepcionista INT,
    total DECIMAL(10,2) NOT NULL,
    fecha_venta DATETIME DEFAULT GETDATE()
);

CREATE TABLE Pagos (
    id_pago INT IDENTITY(1,1) PRIMARY KEY,
    id_cita INT NULL, -- Puede ser NULL si es un pago por Venta de Servicio
    id_venta_servicio INT NULL,
    folio_pago VARCHAR(50) UNIQUE NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    metodo_pago VARCHAR(50) DEFAULT 'Pendiente' CHECK (metodo_pago IN ('Efectivo', 'Tarjeta de Crédito', 'Tarjeta de Débito', 'Transferencia', 'Pendiente')),
    estatus VARCHAR(20) DEFAULT 'Pendiente' CHECK (estatus IN ('Pendiente', 'Pagado', 'Reembolsado')),
    fecha_pago DATETIME NULL
);

CREATE TABLE Reembolsos (
    id_reembolso INT IDENTITY(1,1) PRIMARY KEY,
    id_pago INT UNIQUE,
    costo_original DECIMAL(10,2) NOT NULL,
    politica_aplicada VARCHAR(150) NOT NULL, -- Razón de la política
    porcentaje_devolucion INT NOT NULL,
    monto_penalizacion DECIMAL(10,2) NOT NULL,
    monto_reembolsado DECIMAL(10,2) NOT NULL,
    fecha_procesamiento DATETIME DEFAULT GETDATE()
);

-- ============================================================================
-- 7. LABORATORIO CLÍNICO
-- ============================================================================
CREATE TABLE Resultados_Laboratorio (
    id_laboratorio INT IDENTITY(1,1) PRIMARY KEY,
    id_paciente INT,
    id_doctor_solicitante INT,
    fecha_estudio DATE NOT NULL,
    observaciones TEXT,
    fecha_subida DATETIME DEFAULT GETDATE()
);

CREATE TABLE Detalle_Laboratorio (
    id_detalle INT IDENTITY(1,1) PRIMARY KEY,
    id_laboratorio INT,
    estudio VARCHAR(150) NOT NULL,
    resultado DECIMAL(8,2) NOT NULL,
    unidades VARCHAR(30) NOT NULL,
    valores_referencia VARCHAR(50) NOT NULL,
    estado VARCHAR(20) DEFAULT 'Normal' CHECK (estado IN ('Normal', 'Elevado', 'Bajo', 'Crítico'))
);

-- ============================================================================
-- 8. FARMACIA: INVENTARIO, SURTIDO Y VENTAS (Admite a no pacientes)
-- ============================================================================
CREATE TABLE Proveedores (
    id_proveedor INT IDENTITY(1,1) PRIMARY KEY,
    nombre_empresa VARCHAR(150) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    activo BIT DEFAULT 1
);

CREATE TABLE Medicamentos (
    id_medicamento INT IDENTITY(1,1) PRIMARY KEY,
    nombre_comercial VARCHAR(150) NOT NULL,
    sustancia_activa VARCHAR(150) NOT NULL,
    presentacion VARCHAR(100) NOT NULL,
    precio_compra DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 10,
    id_proveedor INT
);

CREATE TABLE Recetas (
    id_receta INT IDENTITY(1,1) PRIMARY KEY,
    folio_receta VARCHAR(50) UNIQUE NOT NULL,
    id_cita INT UNIQUE,
    id_doctor INT,
    id_paciente INT,
    estatus_surtido VARCHAR(50) DEFAULT 'Pendiente' CHECK (estatus_surtido IN ('Pendiente', 'Surtido Parcial', 'Surtido Completo')),
    fecha_emision DATETIME DEFAULT GETDATE()
);

CREATE TABLE Detalle_Receta (
    id_detalle_receta INT IDENTITY(1,1) PRIMARY KEY,
    id_receta INT,
    id_medicamento INT,
    cantidad_recetada INT NOT NULL,
    dosis VARCHAR(100) NOT NULL
);

CREATE TABLE Ventas_Farmacia (
    id_venta INT IDENTITY(1,1) PRIMARY KEY,
    folio_venta VARCHAR(50) UNIQUE NOT NULL,
    id_receta INT NULL,
    id_paciente INT NULL, -- NULL para ventas al público en general
    id_empleado_farmacia INT,
    total DECIMAL(10,2) NOT NULL,
    fecha_venta DATETIME DEFAULT GETDATE()
);

CREATE TABLE Detalle_Venta_Farmacia (
    id_detalle_venta INT IDENTITY(1,1) PRIMARY KEY,
    id_venta INT,
    id_medicamento INT,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

-- ============================================================================
-- 9. AUDITORÍA Y BITÁCORAS SEGÚN PDF
-- ============================================================================
-- Las bitácoras solo permitirán SELECT e INSERT (Se configura en MS SQL Server con: 
-- GRANT SELECT, INSERT ON Bitacora_Citas TO [Rol_Recepcionista];)

CREATE TABLE Bitacora_Citas (
    id_bitacora INT IDENTITY(1,1) PRIMARY KEY,
    id_cita INT NULL,
    folio_cita VARCHAR(50) NOT NULL,
    doctor_nombre VARCHAR(150) NULL,
    estatus_consulta VARCHAR(50) NOT NULL, -- Atendida / No Asistió / Cancelada
    especialidad VARCHAR(100) NULL,
    consultorio VARCHAR(50) NULL,
    costo DECIMAL(10,2) NULL,
    politica_cancela VARCHAR(150) NULL,
    monto_devuelto DECIMAL(10,2) NULL,
    fecha_registro DATETIME DEFAULT GETDATE()
);

CREATE TABLE Bitacora_Historial_Medico (
    id_bitacora INT IDENTITY(1,1) PRIMARY KEY,
    id_paciente INT NOT NULL,
    curp_paciente VARCHAR(18) NOT NULL,
    id_doctor_modificador INT NULL,
    accion VARCHAR(100) NOT NULL, -- "Creación Expediente", "Nueva Consulta"
    notas_auditoria TEXT,
    fecha_modificacion DATETIME DEFAULT GETDATE()
);

-- Llaves Foráneas de Recepcionistas
ALTER TABLE Recepcionistas 
ADD CONSTRAINT FK_Recep_Usuario FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE SET NULL;

-- Llaves Foráneas de Consultorios
ALTER TABLE Consultorios 
ADD CONSTRAINT FK_Cons_DoctorActual FOREIGN KEY (id_doctor_actual) REFERENCES Doctores(id_doctor);

-- Llaves Foráneas de Doctores
ALTER TABLE Doctores 
ADD CONSTRAINT FK_Doc_Usuario FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE SET NULL;
ALTER TABLE Doctores 
ADD CONSTRAINT FK_Doc_Especialidad FOREIGN KEY (id_especialidad) REFERENCES Especialidades(id_especialidad);
ALTER TABLE Doctores 
ADD CONSTRAINT FK_Doc_Consultorio FOREIGN KEY (id_consultorio) REFERENCES Consultorios(id_consultorio);

-- Llaves Foráneas de Horarios
ALTER TABLE Horarios_Doctores 
ADD CONSTRAINT FK_Horario_Doctor FOREIGN KEY (id_doctor) REFERENCES Doctores(id_doctor) ON DELETE CASCADE;

-- Llaves Foráneas de Pacientes y Expediente
ALTER TABLE Pacientes 
ADD CONSTRAINT FK_Pac_Usuario FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE SET NULL;

ALTER TABLE Antecedentes_Medicos 
ADD CONSTRAINT FK_Ant_Paciente FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente) ON DELETE CASCADE;

-- Llaves Foráneas de Citas
ALTER TABLE Citas 
ADD CONSTRAINT FK_Cita_Paciente FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente);
ALTER TABLE Citas 
ADD CONSTRAINT FK_Cita_Doctor FOREIGN KEY (id_doctor) REFERENCES Doctores(id_doctor);
ALTER TABLE Citas 
ADD CONSTRAINT FK_Cita_Especialidad FOREIGN KEY (id_especialidad) REFERENCES Especialidades(id_especialidad);

ALTER TABLE Registro_Llegadas 
ADD CONSTRAINT FK_Llegada_Cita FOREIGN KEY (id_cita) REFERENCES Citas(id_cita) ON DELETE CASCADE;
ALTER TABLE Registro_Llegadas 
ADD CONSTRAINT FK_Llegada_Recepcionista FOREIGN KEY (id_recepcionista) REFERENCES Recepcionistas(id_recepcionista);

ALTER TABLE Consultas_Expediente 
ADD CONSTRAINT FK_ConsExp_Cita FOREIGN KEY (id_cita) REFERENCES Citas(id_cita) ON DELETE CASCADE;
ALTER TABLE Consultas_Expediente 
ADD CONSTRAINT FK_ConsExp_Paciente FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente);

-- Llaves Foráneas de Finanzas y Servicios
ALTER TABLE Cortes_Caja 
ADD CONSTRAINT FK_Corte_Recep FOREIGN KEY (id_recepcionista) REFERENCES Recepcionistas(id_recepcionista);

ALTER TABLE Ventas_Servicios 
ADD CONSTRAINT FK_VServ_Paciente FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente);
ALTER TABLE Ventas_Servicios 
ADD CONSTRAINT FK_VServ_Recep FOREIGN KEY (id_recepcionista) REFERENCES Recepcionistas(id_recepcionista);

ALTER TABLE Pagos 
ADD CONSTRAINT FK_Pago_Cita FOREIGN KEY (id_cita) REFERENCES Citas(id_cita) ON DELETE CASCADE;
ALTER TABLE Pagos 
ADD CONSTRAINT FK_Pago_VentaServ FOREIGN KEY (id_venta_servicio) REFERENCES Ventas_Servicios(id_venta_servicio) ON DELETE CASCADE;

ALTER TABLE Reembolsos 
ADD CONSTRAINT FK_Reem_Pago FOREIGN KEY (id_pago) REFERENCES Pagos(id_pago);

-- Llaves Foráneas de Laboratorio
ALTER TABLE Resultados_Laboratorio 
ADD CONSTRAINT FK_Lab_Paciente FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente);
ALTER TABLE Resultados_Laboratorio 
ADD CONSTRAINT FK_Lab_Doctor FOREIGN KEY (id_doctor_solicitante) REFERENCES Doctores(id_doctor);

ALTER TABLE Detalle_Laboratorio 
ADD CONSTRAINT FK_DetLab_Laboratorio FOREIGN KEY (id_laboratorio) REFERENCES Resultados_Laboratorio(id_laboratorio) ON DELETE CASCADE;

-- Llaves Foráneas de Farmacia
ALTER TABLE Medicamentos 
ADD CONSTRAINT FK_Med_Proveedor FOREIGN KEY (id_proveedor) REFERENCES Proveedores(id_proveedor) ON DELETE SET NULL;

ALTER TABLE Recetas 
ADD CONSTRAINT FK_Receta_Cita FOREIGN KEY (id_cita) REFERENCES Citas(id_cita);
ALTER TABLE Recetas 
ADD CONSTRAINT FK_Receta_Doctor FOREIGN KEY (id_doctor) REFERENCES Doctores(id_doctor);
ALTER TABLE Recetas 
ADD CONSTRAINT FK_Receta_Paciente FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente);

ALTER TABLE Detalle_Receta 
ADD CONSTRAINT FK_DetRec_Receta FOREIGN KEY (id_receta) REFERENCES Recetas(id_receta) ON DELETE CASCADE;
ALTER TABLE Detalle_Receta 
ADD CONSTRAINT FK_DetRec_Med FOREIGN KEY (id_medicamento) REFERENCES Medicamentos(id_medicamento);

ALTER TABLE Ventas_Farmacia 
ADD CONSTRAINT FK_VentaFarm_Receta FOREIGN KEY (id_receta) REFERENCES Recetas(id_receta);
ALTER TABLE Ventas_Farmacia 
ADD CONSTRAINT FK_VentaFarm_Paciente FOREIGN KEY (id_paciente) REFERENCES Pacientes(id_paciente);
ALTER TABLE Ventas_Farmacia 
ADD CONSTRAINT FK_VentaFarm_Empleado FOREIGN KEY (id_empleado_farmacia) REFERENCES Usuarios(id_usuario);

ALTER TABLE Detalle_Venta_Farmacia 
ADD CONSTRAINT FK_DetVenta_Venta FOREIGN KEY (id_venta) REFERENCES Ventas_Farmacia(id_venta) ON DELETE CASCADE;
ALTER TABLE Detalle_Venta_Farmacia 
ADD CONSTRAINT FK_DetVenta_Med FOREIGN KEY (id_medicamento) REFERENCES Medicamentos(id_medicamento);