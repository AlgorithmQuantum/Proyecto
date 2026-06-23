from flask import Blueprint, render_template, request, jsonify
from utils.decorador import login_requerido, rol_requerido
from database.db import get_coneccion
import pyodbc

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_requerido
@rol_requerido("Admin")
def admin_dashboard():
    return render_template("administracion/inicioAdmin.html")

@admin_bp.route("/bitacoras")
@login_requerido
@rol_requerido("Admin")
def admin_bitacoras():
    return render_template("administracion/bitacorasAdmin.html")

@admin_bp.route("/doctores")
@login_requerido
@rol_requerido("Admin")
def admin_doctores():
    return render_template("administracion/doctores.html")

@admin_bp.route("/recepcion")
@login_requerido
@rol_requerido("Admin")
def admin_recepcion():
    return render_template("administracion/recepcion.html")

@admin_bp.route("/pacientes")
@login_requerido
@rol_requerido("Admin")
def admin_pacientes():
    return render_template("administracion/pacientes.html")

@admin_bp.route("/catalogos")
@login_requerido
@rol_requerido("Admin")
def admin_catalogos():
    return render_template("administracion/catalogos.html")

@admin_bp.route("/farmacia")
@login_requerido
@rol_requerido("Admin")
def admin_farmacia():
    return render_template("administracion/farmacia.html")

@admin_bp.route("/api/doctores/<int:id_doctor>/baja", methods=["POST"])
@login_requerido
@rol_requerido("Admin")
def dar_baja_doctor(id_doctor):
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()

            # 1. Verificar si tiene citas pendientes a futuro
            cursor.execute("""
                SELECT COUNT(*) FROM CITA 
                WHERE Id_doctor = ? AND Estatus = 1 AND Fecha_cita >= CAST(GETDATE() AS DATE)
            """, id_doctor)
            citas_pendientes = cursor.fetchone()[0]

            if citas_pendientes > 0:
                return jsonify({
                    "error": f"No se puede dar de baja. El doctor tiene {citas_pendientes} citas pendientes por atender."
                }), 400

            # 2. Dar de baja actualizando la tabla USUARIO (No se usa DELETE)
            cursor.execute("""
                UPDATE u SET u.Activo = 0 
                FROM USUARIO u
                JOIN EMPLEADO e ON u.Id_usuario = e.Id_usuario
                JOIN DOCTOR d ON e.Id_empleado = d.Id_empleado
                WHERE d.Id_doctor = ?
            """, id_doctor)
            
            conn.commit()
            
        return jsonify({"mensaje": "Doctor dado de baja exitosamente (Inactivo)."}), 200

    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500
    
@admin_bp.route("/especialidades")
@login_requerido
@rol_requerido("Admin")
def admin_especialidades():
    return render_template("administracion/especialidades.html")

@admin_bp.route("/api/bitacora/global", methods=["GET"])
@login_requerido
@rol_requerido("Admin")
def obtener_bitacora_global():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            # Consultamos la vista de la base de datos
            cursor.execute("""
                SELECT 
                    Id_bitacora, 
                    CONVERT(VARCHAR, FechaMovimiento, 120) AS FechaMovimiento, 
                    FolioCita, 
                    CONVERT(VARCHAR, Fecha_cita, 23) AS Fecha_cita, 
                    CASE WHEN Estatus = 1 THEN 'Agendada/Activa' 
                         WHEN Estatus = 0 THEN 'Cancelada/Anulada' 
                         ELSE 'Eliminada' END AS Estatus,
                    Doctor, 
                    Especialidad, 
                    Paciente
                FROM VW_Bitacora_Citas
                ORDER BY Id_bitacora DESC
            """)
            columnas = [column[0] for column in cursor.description]
            bitacora = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

        return jsonify(bitacora), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/api/lista-doctores", methods=["GET"])
@login_requerido
@rol_requerido("Admin")
def obtener_lista_doctores():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    d.Id_doctor,
                    e.Nombre + ' ' + e.Apellido_Paterno AS NombreCompleto,
                    e.Correo,
                    esp.Nombre AS Especialidad,
                    ISNULL(con.Numero, 'Sin asignar') AS Consultorio,
                    u.Activo
                FROM DOCTOR d
                JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
                JOIN USUARIO u ON e.Id_usuario = u.Id_usuario
                JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
                LEFT JOIN CONSULTORIO con ON d.Id_doctor = con.Id_Doctor
                ORDER BY e.Nombre
            """)
            columnas = [column[0] for column in cursor.description]
            doctores = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

        return jsonify(doctores), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/dashboard-kpis", methods=["GET"])
@login_requerido
@rol_requerido("Admin")
def dashboard_kpis():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            # KPI 1: Total Pacientes
            cursor.execute("SELECT COUNT(*) FROM PACIENTE")
            pacientes = cursor.fetchone()[0]
            # KPI 2: Total Doctores
            cursor.execute("SELECT COUNT(*) FROM DOCTOR d JOIN EMPLEADO e ON d.Id_empleado=e.Id_empleado JOIN USUARIO u ON e.Id_usuario=u.Id_usuario WHERE u.Activo=1")
            doctores = cursor.fetchone()[0]
            # KPI 3: Citas de Hoy
            cursor.execute("SELECT COUNT(*) FROM CITA WHERE Fecha_cita = CAST(GETDATE() AS DATE)")
            citas_hoy = cursor.fetchone()[0]
            # KPI 4: Ingresos del mes (De los tickets pagados)
            cursor.execute("SELECT ISNULL(SUM(Monto_total), 0) FROM TICKET WHERE Estatus_pago = 'Pagado' AND MONTH(Fecha) = MONTH(GETDATE())")
            ingresos = cursor.fetchone()[0]

        return jsonify({"pacientes": pacientes, "doctores": doctores, "citas_hoy": citas_hoy, "ingresos": float(ingresos)}), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/api/lista-recepcion", methods=["GET"])
@login_requerido
@rol_requerido("Admin")
def lista_recepcion():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    r.Id_Recepcionista, e.Nombre + ' ' + e.Apellido_Paterno AS Nombre,
                    e.Correo, r.Turno, u.Activo 
                FROM RECEPCIONISTA r
                JOIN EMPLEADO e ON r.Id_empleado = e.Id_empleado
                JOIN USUARIO u ON e.Id_usuario = u.Id_usuario
            """)
            columnas = [column[0] for column in cursor.description]
            datos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        return jsonify(datos), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/api/lista-farmacia", methods=["GET"])
@login_requerido
@rol_requerido("Admin")
def lista_farmacia():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Id_medicamento, Nombre, Descripcion, Concentracion, Precio, Stock FROM MEDICAMENTO")
            columnas = [column[0] for column in cursor.description]
            datos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        return jsonify(datos), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/api/lista-especialidades", methods=["GET"])
@login_requerido
@rol_requerido("Admin")
def lista_especialidades():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Id_especialidad, Nombre, Costo_Consulta, Descripcion FROM ESPECIALIDAD")
            columnas = [column[0] for column in cursor.description]
            datos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        return jsonify(datos), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/api/lista-catalogos", methods=["GET"])
@login_requerido
@rol_requerido("Admin")
def lista_catalogos():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.Numero, c.Piso, e.Nombre + ' ' + e.Apellido_Paterno AS Doctor, esp.Nombre AS Especialidad
                FROM CONSULTORIO c
                LEFT JOIN DOCTOR d ON c.Id_Doctor = d.Id_doctor
                LEFT JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
                LEFT JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
            """)
            columnas = [column[0] for column in cursor.description]
            datos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        return jsonify(datos), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500
    
@admin_bp.route("/api/bitacora/historial-medico", methods=["GET"])
@login_requerido
@rol_requerido("Admin")
def bitacora_historial_medico():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    CONVERT(VARCHAR, Fecha_Modificacion, 120) AS Fecha_Modificacion,
                    'PAC-' + CAST(Id_paciente AS VARCHAR) AS Id_paciente,
                    Medico_Modifico,
                    Campo_Alterado,
                    Valor_Anterior,
                    Nuevo_Valor
                FROM BITACORA_HISTORIAL
                ORDER BY Fecha_Modificacion DESC
            """)
            columnas = [column[0] for column in cursor.description]
            datos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        return jsonify(datos), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/api/lista-pacientes", methods=["GET"])
@login_requerido
@rol_requerido("Admin")
def lista_pacientes():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    p.Id_paciente,
                    p.Nombre + ' ' + p.Apellido_Paterno AS NombreCompleto,
                    p.Curp,
                    p.Correo,
                    p.Telefono,
                    ISNULL(p.Edad, DATEDIFF(YEAR, p.Fecha_nacimiento, GETDATE())) AS Edad,
                    u.Activo
                FROM PACIENTE p
                JOIN USUARIO u ON p.Id_usuario = u.Id_usuario
            """)
            columnas = [column[0] for column in cursor.description]
            datos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        return jsonify(datos), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500