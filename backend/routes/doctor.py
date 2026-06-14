from flask import Blueprint, render_template, session, request, redirect
from utils.decorador import login_requerido, rol_requerido
from database.db import get_coneccion
from datetime import datetime, timedelta

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")

def td_to_time(val):
    """Helper para convertir timedelta de SQL a objeto de tiempo"""
    if isinstance(val, timedelta):
        total = int(val.total_seconds())
        from datetime import time as dt_time
        return dt_time(total // 3600, (total % 3600) // 60)
    return val

# ── 1. DASHBOARD ─────────────────────────────────────────────────────────────
@doctor_bp.route("/dashboard")
@login_requerido
@rol_requerido("Doctor")
def dashboard():
    # Tu lógica principal del dashboard ya está en dashboard.py, 
    # redirigimos para no duplicar código
    return redirect("/dashboard")

# ── 2. PACIENTES Y EXPEDIENTE ────────────────────────────────────────────────
@doctor_bp.route("/pacientes")
@login_requerido
@rol_requerido("Doctor")
def pacientes():
    id_empleado = session.get("id_entidad")
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Id_doctor FROM DOCTOR WHERE Id_empleado = ?", id_empleado)
        row = cursor.fetchone()
        id_doctor = row[0] if row else None

        cursor.execute("""
            SELECT 
                p.Id_paciente, p.Nombre, p.Apellido_Paterno, p.Correo,
                ISNULL(p.Edad, DATEDIFF(YEAR, p.Fecha_nacimiento, GETDATE())) AS Edad,
                MAX(c.Fecha_cita) AS ultima_consulta,
                (SELECT TOP 1 CASE WHEN t.Id_receta IS NOT NULL THEN 'Estable' ELSE 'En Tratamiento' END 
                 FROM CITA t WHERE t.Id_paciente = p.Id_paciente ORDER BY t.Fecha_cita DESC) AS Estado
            FROM PACIENTE p
            JOIN CITA c ON p.Id_paciente = c.Id_paciente
            WHERE c.Id_doctor = ?
            GROUP BY p.Id_paciente, p.Nombre, p.Apellido_Paterno, p.Correo, p.Fecha_nacimiento, p.Edad
            ORDER BY p.Apellido_Paterno
        """, id_doctor)
        lista_pacientes = cursor.fetchall()
    return render_template("doctor/pacientesDoctor.html", pacientes=lista_pacientes, nombre_completo=session.get("nombre_completo"))

@doctor_bp.route("/expediente/<int:id_paciente>")
@login_requerido
@rol_requerido("Doctor")
def expediente(id_paciente):
    with get_coneccion() as conn:
        cursor = conn.cursor()
        
        # USAMOS LA VISTA DE TU COMPAÑERO: Mucho más limpio que hacer JOINs manuales
        cursor.execute("SELECT * FROM VW_Historial_Medico WHERE Id_paciente = ?", id_paciente)
        paciente = cursor.fetchone()
        
        # Obtenemos las consultas...
        # Traer datos demográficos y somatometría del paciente
        cursor.execute("""
            SELECT 
                P.Id_paciente, P.Nombre, P.Apellido_Paterno, P.Apellido_Materno, 
                HM.Id_historial, HM.Tipo_sangre, HM.Estatura, HM.Peso, HM.Edad, HM.Alergias
            FROM PACIENTE P
            LEFT JOIN HISTORIA_MEDICO HM ON P.Id_paciente = HM.Id_paciente
            WHERE P.Id_paciente = ?
        """, id_paciente)
        paciente = cursor.fetchone()

        # Traer historial de consultas pasadas
        cursor.execute("""
            SELECT c.Fecha_cita, esp.Nombre AS Especialidad, r.Diagnostico
            FROM CITA c
            JOIN DOCTOR d ON c.Id_doctor = d.Id_doctor
            JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
            LEFT JOIN RECETA r ON c.Id_receta = r.Id_receta
            WHERE c.Id_paciente = ? AND c.Estatus = 1 AND c.Id_receta IS NOT NULL
            ORDER BY c.Fecha_cita DESC
        """, id_paciente)
        consultas = cursor.fetchall()

    return render_template("doctor/expediente.html", paciente=paciente)

# ── 3. AGENDA Y CITAS ────────────────────────────────────────────────────────
@doctor_bp.route("/agenda")
@login_requerido
@rol_requerido("Doctor")
def agenda():
    id_empleado = session.get("id_entidad")
    fecha_param = request.args.get("fecha", datetime.now().strftime("%Y-%m-%d"))
    
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.Id_doctor, esp.Nombre, con.Numero
            FROM DOCTOR d
            JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
            LEFT JOIN CONSULTORIO con ON d.Id_doctor = con.Id_Doctor
            WHERE d.Id_empleado = ?
        """, id_empleado)
        doc_info = cursor.fetchone()
        id_doctor = doc_info[0] if doc_info else None

        cursor.execute("""
            SELECT c.Id_cita, c.hora_cita, c.Estatus, c.Id_receta, p.Id_paciente,
                   p.Nombre + ' ' + p.Apellido_Paterno AS nombre_paciente
            FROM CITA c
            JOIN PACIENTE p ON c.Id_paciente = p.Id_paciente
            WHERE c.Id_doctor = ? AND c.Fecha_cita = ?
            ORDER BY c.hora_cita
        """, (id_doctor, fecha_param))
        citas_agenda = cursor.fetchall()

    fecha_dt = datetime.strptime(fecha_param, "%Y-%m-%d")
    dias_es = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    meses_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    fecha_texto = f"{dias_es[fecha_dt.weekday()+1 if fecha_dt.weekday()<6 else 0]}, {fecha_dt.day} de {meses_es[fecha_dt.month-1]}"

    return render_template("doctor/agendaDoctor.html", citas=citas_agenda, fecha_actual=fecha_param, fecha_texto=fecha_texto, doc_info=doc_info, nombre_completo=session.get("nombre_completo"))

# ── 4. RECETAS ───────────────────────────────────────────────────────────────
@doctor_bp.route("/recetas/<int:id_cita>")
@login_requerido
@rol_requerido("Doctor")
def crearReceta(id_cita):
    # Obtener los datos de la cita y paciente para pre-llenar la receta
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                c.Id_cita, c.Fecha_cita, 
                p.Nombre + ' ' + p.Apellido_Paterno AS Paciente,
                ISNULL(p.Edad, DATEDIFF(YEAR, p.Fecha_nacimiento, GETDATE())) AS Edad,
                d.Cedula_General, esp.Nombre AS Especialidad,
                e.Nombre + ' ' + e.Apellido_Paterno AS Doctor
            FROM CITA c
            JOIN PACIENTE p ON c.Id_paciente = p.Id_paciente
            JOIN DOCTOR d ON c.Id_doctor = d.Id_doctor
            JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
            JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
            WHERE c.Id_cita = ?
        """, id_cita)
        cita_info = cursor.fetchone()

    return render_template("doctor/recetasDoctor.html", cita=cita_info, nombre_completo=session.get("nombre_completo"))

# ── 5. PERFIL, LABORATORIO Y AJUSTES ─────────────────────────────────────────
@doctor_bp.route("/perfil")
@login_requerido
@rol_requerido("Doctor")
def perfil():
    id_empleado = session.get("id_entidad")
    with get_coneccion() as conn:
        cursor = conn.cursor()
        
        # Se corrigió esp.Costo_Consulta y se agregaron valores NULL 
        # a los campos que no existen en tus tablas para evitar el error 500
        cursor.execute("""
            SELECT 
                e.Nombre, 
                e.Apellido_Paterno, 
                e.Apellido_Materno, 
                e.CURP, 
                NULL AS Fecha_nacimiento, 
                e.Telefono, 
                e.Correo,
                d.Id_doctor, 
                esp.Nombre AS especialidad, 
                NULL AS Cedula_General, 
                NULL AS Cedula_Especialidad, 
                NULL AS Universidad, 
                esp.Costo_Consulta,
                con.Numero AS consultorio_num, 
                con.Piso
            FROM DOCTOR d
            JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
            JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
            LEFT JOIN CONSULTORIO con ON d.Id_doctor = con.Id_Doctor
            WHERE d.Id_empleado = ?
        """, id_empleado)
        medico = cursor.fetchone()
        
    return render_template("doctor/perfilDoctor.html", medico=medico, nombre_completo=session.get("nombre_completo"))

@doctor_bp.route("/laboratorio")
@login_requerido
@rol_requerido("Doctor")
def laboratorio():
    # Renderizado estático adaptado para pasar el nombre de sesión
    return render_template("doctor/resultadosLab.html", nombre_completo=session.get("nombre_completo"))

@doctor_bp.route("/ajustes")
@login_requerido
@rol_requerido("Doctor")
def ajustes():
    # Renderizado estático adaptado para pasar el nombre de sesión
    return render_template("doctor/ajustesDoctor.html", nombre_completo=session.get("nombre_completo"))