from flask import Blueprint, render_template, session, request, redirect, jsonify
from utils.decorador import login_requerido, rol_requerido
from database.db import get_coneccion
import pyodbc
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


@doctor_bp.route("/api/receta/generar", methods=["POST"])
@login_requerido
@rol_requerido("Doctor")
def generar_receta():
    data = request.json
    id_cita = data.get("id_cita")
    diagnostico = data.get("diagnostico")
    tratamiento = data.get("tratamiento")
    indicaciones = data.get("indicaciones")
    medicamentos = data.get("medicamentos", []) # Lista de diccionarios
    
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()

            # 1. Validar la fecha de la cita y que no tenga receta ya
            cursor.execute("""
                SELECT c.Fecha_cita, c.Id_paciente, c.Id_doctor, c.Id_receta 
                FROM CITA c WHERE c.Id_cita = ?
            """, id_cita)
            cita = cursor.fetchone()

            if not cita:
                return jsonify({"error": "Cita no encontrada"}), 404
            if cita[3] is not None:
                return jsonify({"error": "Esta cita ya fue atendida (ya cuenta con receta)."}), 400
            
            # Validación de fecha estricta pedida en la rúbrica
            if str(cita[0]) != datetime.now().strftime("%Y-%m-%d"):
                return jsonify({"error": "Solo se pueden generar recetas el día exacto de la cita médica."}), 400

            id_paciente, id_doctor = cita[1], cita[2]

            # 2. Generar la Receta
            cursor.execute("""
                INSERT INTO RECETA (Id_paciente, Id_doctor, Fecha, Diagnostico, Tratamiento, Indicaciones)
                OUTPUT INSERTED.Id_receta
                VALUES (?, ?, GETDATE(), ?, ?, ?)
            """, id_paciente, id_doctor, diagnostico, tratamiento, indicaciones)
            id_receta = cursor.fetchone()[0]

            # 3. Insertar Medicamentos
            for med in medicamentos:
                cursor.execute("""
                    INSERT INTO RECETA_MEDICINA (Id_receta, Id_medicamento, Dosis, Frecuencia, Indicaciones, Cantidad)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, id_receta, med["id_medicamento"], med["dosis"], med["frecuencia"], med["indicaciones"], med.get("cantidad", 1))

            # 4. MARCAR COMO ATENDIDA (Asignando la receta a la cita)
            cursor.execute("UPDATE CITA SET Id_receta = ? WHERE Id_cita = ?", id_receta, id_cita)
            
            conn.commit()
            
        return jsonify({"mensaje": "Receta generada y cita marcada como ATENDIDA.", "id_receta": id_receta}), 201

    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500

@doctor_bp.route("/api/paciente/bitacora", methods=["GET"])
@login_requerido
@rol_requerido("Doctor")
def bitacora_paciente():
    parametro = request.args.get("paciente", "")
    id_empleado = session.get("id_entidad")

    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            
            # Buscamos en la tabla BITACORA_CITA haciendo joins con CITA, PACIENTE y ESPECIALIDAD
            cursor.execute("""
                SELECT 
                    b.Id_bitacora,
                    b.Fecha_cambio AS Fecha_Movimiento,
                    c.Id_cita AS Folio_Cita,
                    c.Fecha_cita,
                    CASE WHEN b.Estatus_cita = 1 THEN 'Activa/Atendida' ELSE 'Cancelada/No Acudió' END AS Estatus_Cita,
                    e.Nombre + ' ' + e.Apellido_Paterno AS Nombre_Doctor,
                    esp.Nombre AS Especialidad,
                    esp.Costo_Consulta AS Costo,
                    p.Nombre + ' ' + p.Apellido_Paterno AS Nombre_Paciente,
                    ISNULL(r.Diagnostico, 'Sin diagnóstico') AS Diagnostico
                FROM BITACORA_CITA b
                JOIN CITA c ON b.Id_cita = c.Id_cita
                JOIN DOCTOR d ON c.Id_doctor = d.Id_doctor
                JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
                JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
                JOIN PACIENTE p ON c.Id_paciente = p.Id_paciente
                LEFT JOIN RECETA r ON c.Id_receta = r.Id_receta
                WHERE d.Id_empleado = ? AND 
                      (CAST(p.Id_paciente AS VARCHAR) = ? OR p.Nombre LIKE '%' + ? + '%')
                ORDER BY b.Fecha_cambio DESC
            """, id_empleado, parametro, parametro)
            
            columnas = [column[0] for column in cursor.description]
            bitacora = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

        return jsonify(bitacora), 200

    except pyodbc.Error as err:
        return jsonify({"error": str(err)}), 500

@doctor_bp.route("/api/paciente/<int:id_paciente>/historial-medico", methods=["GET"])
@login_requerido
@rol_requerido("Doctor")
def ver_historial_medico(id_paciente):
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            # Esta consulta llama directamente a la vista VW_Historial_Medico que ya tienes en tu SQL
            cursor.execute("""
                SELECT 
                    Nombre, 
                    Apellido_Paterno, 
                    Tipo_sangre, 
                    Estatura, 
                    Peso, 
                    Edad, 
                    Alergias 
                FROM VW_Historial_Medico 
                WHERE Id_paciente = ?
            """, id_paciente)
            
            fila = cursor.fetchone()
            if not fila:
                return jsonify({"error": "No se encontró historial para este paciente"}), 404
                
            columnas = [column[0] for column in cursor.description]
            historial = dict(zip(columnas, fila))

        return jsonify(historial), 200

    except pyodbc.Error as err:
        return jsonify({"error": str(err)}), 500

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

@doctor_bp.route("/api/mis-recetas", methods=["GET"])
@login_requerido
@rol_requerido("Doctor")
def obtener_recetas_doctor():
    # Parámetros de búsqueda permitidos por la rúbrica
    busqueda = request.args.get("busqueda", "")
    id_empleado = session.get("id_entidad")

    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    r.Id_receta AS Num_Receta,
                    r.Fecha,
                    p.Nombre + ' ' + p.Apellido_Paterno AS Nombre_Paciente,
                    e.Nombre + ' ' + e.Apellido_Paterno AS Nombre_Medico,
                    r.Diagnostico,
                    r.Tratamiento,
                    r.Indicaciones AS Observaciones,
                    -- Subconsulta para agrupar medicamentos en un solo string
                    STUFF((SELECT ', ' + m.Nombre + ' (' + rm.Frecuencia + ')' 
                           FROM RECETA_MEDICINA rm 
                           JOIN MEDICAMENTO m ON rm.Id_medicamento = m.Id_medicamento 
                           WHERE rm.Id_receta = r.Id_receta 
                           FOR XML PATH('')), 1, 2, '') AS Medicamentos
                FROM RECETA r
                JOIN DOCTOR d ON r.Id_doctor = d.Id_doctor
                JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
                JOIN PACIENTE p ON r.Id_paciente = p.Id_paciente
                WHERE d.Id_empleado = ?
            """
            
            # Filtro dinámico si el usuario busca por fecha o número de receta
            parametros = [id_empleado]
            if busqueda:
                query += " AND (CAST(r.Id_receta AS VARCHAR) = ? OR CAST(r.Fecha AS VARCHAR) = ?)"
                parametros.extend([busqueda, busqueda])
                
            query += " ORDER BY r.Fecha DESC"
            
            cursor.execute(query, parametros)
            columnas = [column[0] for column in cursor.description]
            recetas = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

        return jsonify(recetas), 200

    except pyodbc.Error as err:
        return jsonify({"error": str(err)}), 500