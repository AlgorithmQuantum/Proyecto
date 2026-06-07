from flask import Blueprint, request, render_template, redirect, session, jsonify
import pyodbc
from database.db import get_coneccion
from werkzeug.security import generate_password_hash, check_password_hash
from utils.bitacora import registrar_evento

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


#ruta para logearse
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    usuario = request.form.get("usuario")
    password = request.form.get("password")
    recordar = request.form.get("recordar")

    if not usuario or not password:
        return render_template("login.html", error="Usuario y contraseña son requeridos")

    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            
            # Buscar en tabla USUARIO (por nombre de usuario o email)
            cursor.execute(
                """
                SELECT Id_usuario, usuario, password_hash, Rol, Activo
                FROM USUARIO
                WHERE usuario = ? OR (SELECT Correo FROM PACIENTE WHERE Correo = ?) IS NOT NULL
                   OR (SELECT Correo FROM EMPLEADO WHERE Correo = ?) IS NOT NULL
                """,
                usuario, usuario, usuario
            )
            user = cursor.fetchone()
            
            # Si no se encontró por usuario, buscar por email en PACIENTE o EMPLEADO
            if not user:
                cursor.execute(
                    """
                    SELECT u.Id_usuario, u.usuario, u.password_hash, u.Rol, u.Activo
                    FROM USUARIO u
                    INNER JOIN PACIENTE p ON u.Id_usuario = p.Id_usuario
                    WHERE p.Correo = ?
                    UNION
                    SELECT u.Id_usuario, u.usuario, u.password_hash, u.Rol, u.Activo
                    FROM USUARIO u
                    INNER JOIN EMPLEADO e ON u.Id_usuario = e.Id_usuario
                    WHERE e.Correo = ?
                    """,
                    usuario, usuario
                )
                user = cursor.fetchone()
            
            if not user:
                return render_template("login.html", error="Usuario o contraseña incorrectos")
            
            # Verificar si está activo
            if not user.Activo:
                return render_template("login.html", error="Cuenta inactiva. Contacte al administrador.")
            
            # Verificar contraseña
            if not check_password_hash(user.password_hash, password):
                registrar_evento(usuario, "LOGIN_FALLIDO", "Intento de login con contraseña incorrecta")
                return render_template("login.html", error="Usuario o contraseña incorrectos")
            
            # Obtener datos adicionales según el rol
            datos_extra = {}
            nombre_completo = user.usuario
            id_entidad = None
            
            if user.Rol == 'Paciente':
                cursor.execute(
                    """
                    SELECT Id_paciente, Nombre, Apellido_Paterno, Apellido_Materno, 
                           Correo, Telefono, Curp
                    FROM PACIENTE
                    WHERE Id_usuario = ?
                    """,
                    user.Id_usuario
                )
                paciente = cursor.fetchone()
                if paciente:
                    nombre_completo = f"{paciente.Nombre} {paciente.Apellido_Paterno}"
                    if paciente.Apellido_Materno:
                        nombre_completo += f" {paciente.Apellido_Materno}"
                    id_entidad = paciente.Id_paciente
                    datos_extra = {
                        "id_entidad": paciente.Id_paciente,
                        "correo": paciente.Correo,
                        "telefono": paciente.Telefono,
                        "curp": paciente.Curp
                    }
            
            elif user.Rol in ['Doctor', 'Recepcionista', 'Administrador', 'Farmaceutico']:
                cursor.execute(
                    """
                    SELECT Id_empleado, Nombre, Apellido_Paterno, Apellido_Materno, 
                           Correo, Telefono, Tipo_empleo, Curp
                    FROM EMPLEADO
                    WHERE Id_usuario = ?
                    """,
                    user.Id_usuario
                )
                empleado = cursor.fetchone()
                if empleado:
                    nombre_completo = f"{empleado.Nombre} {empleado.Apellido_Paterno}"
                    if empleado.Apellido_Materno:
                        nombre_completo += f" {empleado.Apellido_Materno}"
                    id_entidad = empleado.Id_empleado
                    datos_extra = {
                        "id_entidad": empleado.Id_empleado,
                        "correo": empleado.Correo,
                        "telefono": empleado.Telefono,
                        "tipo_empleo": empleado.Tipo_empleo,
                        "curp": empleado.Curp
                    }
                    
                    # Si es Doctor, obtener especialidad y consultorio
                    if user.Rol == 'Doctor':
                        cursor.execute(
                            """
                            SELECT esp.Nombre AS Especialidad, esp.Costo_Consulta,
                                   c.Numero AS Consultorio, c.Piso,
                                   h.Hora_Inicio, h.Hora_Fin, h.Dia
                            FROM DOCTOR d
                            INNER JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
                            LEFT JOIN CONSULTORIO c ON d.Id_doctor = c.Id_Doctor
                            LEFT JOIN HORARIO h ON d.Id_Horario = h.Id_Horario
                            WHERE d.Id_empleado = ?
                            """,
                            empleado.Id_empleado
                        )
                        doctor = cursor.fetchone()
                        if doctor:
                            datos_extra["especialidad"] = doctor.Especialidad
                            datos_extra["costo_consulta"] = float(doctor.Costo_Consulta) if doctor.Costo_Consulta else None
                            datos_extra["consultorio"] = doctor.Consultorio
                            datos_extra["piso"] = doctor.Piso
                            datos_extra["horario_inicio"] = str(doctor.Hora_Inicio) if doctor.Hora_Inicio else None
                            datos_extra["horario_fin"] = str(doctor.Hora_Fin) if doctor.Hora_Fin else None
                            datos_extra["dia"] = doctor.Dia
            
            # Actualizar último acceso
            cursor.execute(
                "UPDATE USUARIO SET Ultimo_acceso = GETDATE() WHERE Id_usuario = ?",
                user.Id_usuario
            )
            conn.commit()
            
            # Guardar en sesión
            session.permanent = bool(recordar)
            session["usuario_id"] = user.Id_usuario
            session["id_entidad"] = id_entidad
            session["nombre_completo"] = nombre_completo
            session["rol"] = user.Rol
            session["usuario"] = user.usuario
            session.update(datos_extra)
            
            # Registrar evento exitoso
            registrar_evento(user.usuario, "LOGIN", f"Inicio de sesión exitoso - Rol detectado: {user.Rol}")
            
            # Redirección automática según el rol detectado
            rutas_por_rol = {
                "Doctor": "/dashboard",
                "Recepcionista": "/dashboard",
                "Administrador": "/dashboard",
                "Paciente": "/dashboard",
                "Farmaceutico": "/dashboard"
            }
            
            return redirect(rutas_por_rol.get(user.Rol, "/dashboard"))
            
    except pyodbc.Error as e:
        return render_template("login.html", error=f"Error de base de datos: {str(e)}")

#ruta para salir de sesion 
@auth_bp.route("/logout")
def logout():
    usuario = session.get("usuario", "Desconocido")
    rol = session.get("rol", "Desconocido")
    session.clear()
    registrar_evento(usuario, "LOGOUT", f"Cierre de sesión - Rol: {rol}")
    return redirect("/auth/login")

#ruta para registrarse
# ── Registro de pacientes (público) ───────────────────────────────────────────
@auth_bp.route("/registro", methods=["GET", "POST"])
def registro_form():
    if request.method == "GET":
        return render_template("registro.html")
    
    # Obtener datos del formulario
    nombre = request.form.get("nombre")
    apellido_paterno = request.form.get("apellido_paterno")
    apellido_materno = request.form.get("apellido_materno")
    curp = request.form.get("curp")
    telefono = request.form.get("telefono")
    correo = request.form.get("correo")
    usuario = request.form.get("usuario")
    password = request.form.get("password")
    confirm_password = request.form.get("confirmar_password")
    fecha_nacimiento = request.form.get("fecha_nacimiento")
    tipo_sangre = request.form.get("tipo_sangre")
    alergias = request.form.get("alergias")
    rol = request.form.get("rol", "Paciente")
    
    # Validaciones
    if not all([nombre, apellido_paterno, curp, usuario, password, confirm_password]):
        return render_template("registro.html", error="Todos los campos obligatorios deben ser llenados")
    
    if password != confirm_password:
        return render_template("registro.html", error="Las contraseñas no coinciden")
    
    if len(password) < 6:
        return render_template("registro.html", error="La contraseña debe tener al menos 6 caracteres")
    
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            
            # Verificar si el usuario ya existe
            cursor.execute("SELECT 1 FROM USUARIO WHERE usuario = ?", usuario)
            if cursor.fetchone():
                return render_template("registro.html", error="El nombre de usuario ya existe")
            
            # Verificar si la CURP ya existe
            cursor.execute("SELECT 1 FROM PACIENTE WHERE Curp = ?", curp)
            if cursor.fetchone():
                return render_template("registro.html", error="Ya existe un paciente con esa CURP")
            
            # Verificar si el correo ya existe
            if correo:
                cursor.execute("SELECT 1 FROM PACIENTE WHERE Correo = ?", correo)
                if cursor.fetchone():
                    return render_template("registro.html", error="El correo electrónico ya está registrado")
            
            # Generar hash de contraseña
            password_hash = generate_password_hash(password)
            
            # Usar el procedimiento almacenado para crear paciente
            cursor.execute(
                    """
                    EXEC sp_CrearPaciente
                        @usuario          = ?,
                        @password_hash    = ?,
                        @Nombre           = ?,
                        @Apellido_Paterno = ?,
                        @Apellido_Materno = ?,
                        @Curp             = ?,
                        @Telefono         = ?,
                        @Correo           = ?,
                        @Fecha_nacimiento = ?,
                        @Tipo_sangre      = ?,
                        @Alergias         = ?
                    """,
                    usuario,
                    password_hash,
                    nombre,
                    apellido_paterno,
                    apellido_materno,
                    curp,
                    telefono,
                    correo,           
                    fecha_nacimiento,
                    tipo_sangre,
                    alergias or None  
            )
            
            conn.commit()
            
            registrar_evento(usuario, "REGISTRO", f"Nuevo paciente registrado: {nombre} {apellido_paterno}")
            return redirect("/auth/login?success=Cuenta creada exitosamente. Ahora puedes iniciar sesión.")
            
    except pyodbc.Error as e:
        return render_template("registro.html", error=f"Error de base de datos: {str(e)}")
    

# ── Registro de empleados (solo administradores) ──────────────────────────────
@auth_bp.route("/registro-empleado", methods=["GET", "POST"])
def register_empleado():
    # Verificar que solo administradores puedan crear empleados
    if session.get("rol") not in ("Administrador", "Recepcionista"):
        return redirect("/auth/login")
    
    if request.method == "GET":
        # Obtener especialidades para el select (si es doctor)
        try:
            with get_coneccion() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Id_especialidad, Nombre FROM ESPECIALIDAD ORDER BY Nombre")
                especialidades = cursor.fetchall()
                cursor.execute("SELECT Id_Horario, Dia, Hora_Inicio, Hora_Fin FROM HORARIO ORDER BY Dia, Hora_Inicio")
                horarios = cursor.fetchall()
            return render_template("registroEmpleado.html", especialidades=especialidades, horarios=horarios)
        except pyodbc.Error as e:
            return render_template("registroEmpleado.html", error=f"Error: {str(e)}")
    
    # Obtener datos del formulario
    usuario = request.form.get("usuario")
    password = request.form.get("password")
    rol = request.form.get("rol")
    nombre = request.form.get("nombre")
    apellido_paterno = request.form.get("apellido_paterno")
    apellido_materno = request.form.get("apellido_materno")
    curp = request.form.get("curp")
    correo = request.form.get("correo")
    telefono = request.form.get("telefono")
    tipo_empleo = request.form.get("tipo_empleo", rol)
    fecha_contratacion = request.form.get("fecha_contratacion")
    
    # Validaciones
    if not all([usuario, password, rol, nombre, apellido_paterno, curp, correo, fecha_contratacion]):
        return render_template("registroEmpleado.html", error="Todos los campos obligatorios deben ser llenados")
    
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            
            # Verificar si el usuario ya existe
            cursor.execute("SELECT 1 FROM USUARIO WHERE usuario = ?", usuario)
            if cursor.fetchone():
                return render_template("registroEmpleado.html", error="El nombre de usuario ya existe")
            
            # Verificar si el correo ya existe
            cursor.execute("SELECT 1 FROM EMPLEADO WHERE Correo = ?", correo)
            if cursor.fetchone():
                return render_template("registroEmpleado.html", error="El correo ya está registrado")
            
            # Verificar si la CURP ya existe
            cursor.execute("SELECT 1 FROM EMPLEADO WHERE Curp = ?", curp)
            if cursor.fetchone():
                return render_template("registroEmpleado.html", error="La CURP ya está registrada")
            
            # Generar hash de contraseña
            password_hash = generate_password_hash(password)
            
            # Parámetros adicionales para doctores
            id_especialidad = request.form.get("id_especialidad") if rol == "Doctor" else None
            id_horario = request.form.get("id_horario") if rol == "Doctor" else None
            
            # Usar el procedimiento almacenado para crear empleado
            cursor.execute(
                """
                EXEC sp_CrearEmpleado
                    @usuario = ?,
                    @password_hash = ?,
                    @Rol = ?,
                    @Nombre = ?,
                    @Apellido_Paterno = ?,
                    @Apellido_Materno = ?,
                    @Curp = ?,
                    @Correo = ?,
                    @Telefono = ?,
                    @Tipo_empleo = ?,
                    @Fecha_contratacion = ?,
                    @Id_especialidad = ?,
                    @Id_Horario = ?
                """,
                usuario, password_hash, rol, nombre, apellido_paterno, apellido_materno,
                curp, correo, telefono, tipo_empleo, fecha_contratacion,
                id_especialidad, id_horario
            )
            
            conn.commit()
            
            registrar_evento(usuario, "REGISTRO", f"Nuevo empleado registrado - Rol: {rol}")
            return redirect("/dashboard")
            
    except pyodbc.Error as e:
        return render_template("registroEmpleado.html", error=f"Error de base de datos: {str(e)}")