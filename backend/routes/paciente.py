from flask import Blueprint, render_template, session, redirect, jsonify, request
from utils.decorador import login_requerido, rol_requerido
from database.db import get_coneccion
from datetime import datetime, timedelta

paciente_bp = Blueprint("paciente", __name__, url_prefix="/paciente")

# ==========================================
# 1. VISTAS PRINCIPALES (RENDER TEMPLATES)
# ==========================================

@paciente_bp.route("/dashboard")
@login_requerido
@rol_requerido("Paciente")
def dashboard():
    id_paciente = session.get("id_entidad")
    
    with get_coneccion() as conn:
        cursor = conn.cursor()

        # Ficha médica
        cursor.execute("""
            SELECT p.Nombre, p.Apellido_Paterno, p.Apellido_Materno, p.Correo, p.Telefono,
                   p.Fecha_nacimiento, p.Tipo_sangre, p.Alergias, p.Peso, p.Estatura,
                   ISNULL(p.Edad, DATEDIFF(YEAR, p.Fecha_nacimiento, GETDATE())) AS Edad
            FROM PACIENTE p WHERE p.Id_paciente = ?
        """, id_paciente)
        ficha = cursor.fetchone()

        # Contadores de citas
        cursor.execute("""
            SELECT
                COUNT(CASE WHEN c.Estatus = 1 AND c.Fecha_cita >= CAST(GETDATE() AS DATE) THEN 1 END) AS confirmadas,
                COUNT(CASE WHEN c.Estatus = 1 AND c.Fecha_cita < CAST(GETDATE() AS DATE) AND c.Id_receta IS NOT NULL THEN 1 END) AS completadas,
                COUNT(CASE WHEN c.Estatus = 0 THEN 1 END) AS canceladas
            FROM CITA c WHERE c.Id_paciente = ?
        """, id_paciente)
        contadores = cursor.fetchone()

        # Próximas citas activas (máx 5)
        cursor.execute("""
            SELECT TOP 5 c.Id_cita, c.Fecha_cita, c.hora_cita, c.Hora_Fin, c.Estatus,
                         e.Nombre + ' ' + e.Apellido_Paterno AS nombre_doctor,
                         esp.Nombre AS specialty, con.Numero AS consultorio,
                         ISNULL((SELECT TOP 1 Estatus FROM PAGO p WHERE p.Id_cita = c.Id_cita), 0) AS Pago_Estatus
            FROM CITA c
            JOIN DOCTOR d ON c.Id_doctor = d.Id_doctor
            JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
            JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
            LEFT JOIN CONSULTORIO con ON c.Id_consultorio = con.Id_consultorio
            WHERE c.Id_paciente = ? AND c.Estatus = 1 AND c.Fecha_cita >= CAST(GETDATE() AS DATE)
            ORDER BY c.Fecha_cita, c.hora_cita
        """, id_paciente)
        proximas_citas = cursor.fetchall()

    return render_template(
        "paciente/inicioPaciente.html",
        ficha=ficha,
        contadores=contadores,
        citas=proximas_citas,
        nombre_completo=session.get("nombre_completo")
    )


@paciente_bp.route("/perfil")
@login_requerido
@rol_requerido("Paciente")
def perfil():
    id_paciente = session.get("id_entidad")
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.Nombre, p.Apellido_Paterno, p.Apellido_Materno, p.Correo, p.Telefono,
                   p.Fecha_nacimiento, p.Tipo_sangre, p.Alergias, p.Peso, p.Estatura,
                   ISNULL(p.Edad, DATEDIFF(YEAR, p.Fecha_nacimiento, GETDATE())) AS Edad
            FROM PACIENTE p WHERE p.Id_paciente = ?
        """, id_paciente)
        ficha = cursor.fetchone()
    return render_template("paciente/perfilPaciente.html", ficha=ficha)


@paciente_bp.route("/historial")
@login_requerido
@rol_requerido("Paciente")
def historial():
    id_paciente = session.get("id_entidad")
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 5 c.Id_cita, c.Fecha_cita, c.hora_cita, c.Hora_Fin, c.Estatus,
                         e.Nombre + ' ' + e.Apellido_Paterno AS nombre_doctor,
                         esp.Nombre AS specialty, con.Numero AS consultorio,
                         ISNULL((SELECT TOP 1 Estatus FROM PAGO p WHERE p.Id_cita = c.Id_cita), 0) AS Pago_Estatus
            FROM CITA c
            JOIN DOCTOR d ON c.Id_doctor = d.Id_doctor
            JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
            JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
            LEFT JOIN CONSULTORIO con ON c.Id_consultorio = con.Id_consultorio
            WHERE c.Id_paciente = ? AND c.Estatus = 1 AND c.Fecha_cita >= CAST(GETDATE() AS DATE)
            ORDER BY c.Fecha_cita, c.hora_cita
        """, id_paciente)
        historial_citas = cursor.fetchall()
    return render_template("paciente/historialPaciente.html", historial=historial_citas)


@paciente_bp.route("/citas")
@login_requerido
@rol_requerido("Paciente")
def citas():
    return render_template("paciente/citasPaciente.html")


@paciente_bp.route("/detalles/<int:id_cita>")
@login_requerido
@rol_requerido("Paciente")
def detalles_citas(id_cita):
    return render_template("paciente/detallesCita.html", id_cita=id_cita)


@paciente_bp.route("/comprobante/<int:id_cita>")
@login_requerido
@rol_requerido("Paciente")
def comprobante(id_cita):
    return render_template("paciente/comprobanteCita.html", id_cita=id_cita)


@paciente_bp.route("/cancelacion/<int:id_cita>")
@login_requerido
@rol_requerido("Paciente")
def cancelacion(id_cita):
    return render_template("paciente/cancelarCita.html", id_cita=id_cita)


# ==========================================
# 2. ENDPOINTS DE LA API (RETORNO DE JSON)
# ==========================================

@paciente_bp.route("/api/especialidades")
@login_requerido
def api_especialidades():
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Id_especialidad, Nombre, Costo_Consulta FROM ESPECIALIDAD")
        filas = cursor.fetchall()
        resultado = [{"id_especialidad": r[0], "nombre": r[1], "costo_consulta": float(r[2])} for r in filas]
    return jsonify(resultado)


@paciente_bp.route("/api/doctores/<int:id_especialidad>")
@login_requerido
def api_doctores(id_especialidad):
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.Id_doctor, e.Nombre + ' ' + e.Apellido_Paterno AS nombre_completo,
                   h.Dia, h.Hora_Inicio, h.Hora_Fin
            FROM DOCTOR d
            JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
            JOIN HORARIO h ON d.Id_Horario = h.Id_Horario
            WHERE d.Id_especialidad = ?
        """, id_especialidad)
        filas = cursor.fetchall()
        resultado = [{
            "id_doctor": r[0],
            "nombre_completo": r[1],
            "dia_horario": r[2],
            "hora_inicio": str(r[3]),
            "hora_fin": str(r[4])
        } for r in filas]
    return jsonify(resultado)


@paciente_bp.route("/api/horas-disponibles")
@login_requerido
def api_horas_disponibles():
    id_doctor = request.args.get("id_doctor", type=int)
    fecha_str = request.args.get("fecha") # YYYY-MM-DD
    
    if not id_doctor or not fecha_str:
        return jsonify({"error": "Parámetros faltantes"}), 400

    with get_coneccion() as conn:
        cursor = conn.cursor()
        # Obtener el rango de horas asignadas al médico
        cursor.execute("""
            SELECT h.Hora_Inicio, h.Hora_Fin 
            FROM DOCTOR d 
            JOIN HORARIO h ON d.Id_Horario = h.Id_Horario WHERE d.Id_doctor = ?
        """, id_doctor)
        horario = cursor.fetchone()
        
        if not horario:
            return jsonify({"mensaje": "Médico sin horario configurado"}), 200

        # Obtener horas ocupadas en esa fecha
        cursor.execute("SELECT hora_cita FROM CITA WHERE Id_doctor = ? AND Fecha_cita = ? AND Estatus = 1", (id_doctor, fecha_str))
        ocupadas = [str(r[0])[:5] for r in cursor.fetchall()]

    # Generar bloques de citas de 30 minutos
    slots = []
    inicio = datetime.strptime(str(horario[0])[:5], "%H:%M")
    fin = datetime.strptime(str(horario[1])[:5], "%H:%M")
    
    while inicio < fin:
        hora_actual_str = inicio.strftime("%H:%M")
        slots.append({
            "hora": hora_actual_str,
            "disponible": hora_actual_str not in ocupadas
        })
        inicio += timedelta(minutes=30)

    return jsonify({"slots": slots})


@paciente_bp.route("/api/agendar", methods=["POST"])
@login_requerido
def api_agendar():
    data = request.get_json()
    id_doctor = data.get("id_doctor")
    fecha = data.get("fecha")
    hora_inicio_str = data.get("hora")
    id_paciente = session.get("id_entidad")

    if not all([id_doctor, fecha, hora_inicio_str]):
        return jsonify({"error": "Datos incompletos para agendar"}), 400

    # Calcular Hora Fin de la cita sumando 30 minutos
    formato = "%H:%M"
    if len(hora_inicio_str) > 5:
        hora_inicio_str = hora_inicio_str[:5]
    hora_fin_obj = datetime.strptime(hora_inicio_str, formato) + timedelta(minutes=30)
    hora_fin_str = hora_fin_obj.strftime(formato)

    with get_coneccion() as conn:
        cursor = conn.cursor()
        
        # Asignar un consultorio disponible vinculado al doctor o por defecto
        cursor.execute("SELECT TOP 1 Id_consultorio FROM CONSULTORIO WHERE Id_Doctor = ? ORDER BY Id_consultorio", id_doctor)
        con_row = cursor.fetchone()
        id_consultorio = con_row[0] if con_row else None

        # Insertar cita con Estatus = 1 (Activa)
        cursor.execute("""
            INSERT INTO CITA (Fecha_cita, hora_cita, Hora_Fin, Estatus, Id_doctor, Id_paciente, Id_consultorio)
            OUTPUT INSERTED.Id_cita
            VALUES (?, ?, ?, 1, ?, ?, ?)
        """, (fecha, hora_inicio_str, hora_fin_str, id_doctor, id_paciente, id_consultorio))
        
        id_cita = cursor.fetchone()[0]
        conn.commit()

    return jsonify({"id_cita": id_cita})


@paciente_bp.route("/api/citas/<int:id_cita>")
@login_requerido
def api_citas_detalles(id_cita):
    # Obtenemos quién es el paciente logueado actualmente
    id_paciente_actual = session.get("id_entidad")
    
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            # Traemos la información, incluyendo el c.Id_paciente para validar
            cursor.execute("""
                SELECT c.Id_cita, c.Fecha_cita, c.hora_cita, c.Hora_Fin, c.Estatus,
                       e.Nombre + ' ' + e.Apellido_Paterno AS doctor_nombre, esp.Nombre AS especialidad, esp.Costo_Consulta,
                       con.Piso, con.Numero, p.Nombre + ' ' + p.Apellido_Paterno AS paciente_nombre,
                       c.Id_paciente
                FROM CITA c
                JOIN DOCTOR d ON c.Id_doctor = d.Id_doctor
                JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
                JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
                LEFT JOIN CONSULTORIO con ON c.Id_consultorio = con.Id_consultorio
                JOIN PACIENTE p ON c.Id_paciente = p.Id_paciente
                WHERE c.Id_cita = ?
            """, id_cita)
            r = cursor.fetchone()

            if not r:
                return jsonify({"error": "Cita no encontrada"}), 404
            
            # Si el ID del paciente de la cita no es el mismo que el logueado, lo bloqueamos
            if r[11] != id_paciente_actual:
                return jsonify({"error": "Acceso denegado. Este comprobante pertenece a otro paciente."}), 403

        # Función interna rápida para asegurar que la hora vaya limpia hacia el frontend
        def limpiar_hora(hora_sql):
            if not hora_sql: return "Sin definir"
            hora_str = str(hora_sql)
            if hora_str == "None": return "Sin definir"
            
            # Cortamos estrictamente los primeros 5 caracteres (Ej. '09:00:00' -> '09:00')
            partes = hora_str.split(':')
            if len(partes) >= 2:
                return f"{partes[0].zfill(2)}:{partes[1]}"
            return hora_str
        
        # Consultamos si existe un registro en la tabla PAGO para esta cita
        cursor.execute("SELECT Estatus FROM PAGO WHERE Id_cita = ?", id_cita)
        pago_db = cursor.fetchone()
        
        # Como en BD es un bit (1 o 0), lo traducimos para que el frontend lo entienda
        if pago_db and pago_db[0] == 1:
            estatus_del_pago = "Pagado"
        else:
            estatus_del_pago = "Pendiente"

        # Tu diccionario modificado
        datos = {
            "id_cita": r[0],
            "folio": f"CIT-{r[0]}",
            "estatus": "Activa" if r[4] == 1 else "Cancelada",
            "fecha": str(r[1]),
            "hora_inicio": limpiar_hora(r[2]),
            "hora_fin": limpiar_hora(r[3]),
            "diagnostico": "Por determinar", 
            "doctor": {"nombre_completo": r[5], "especialidad": r[6], "costo_consulta": float(r[7])},
            "consultorio": {"piso": r[8] if r[8] is not None else "PB", "numero": r[9] if r[9] is not None else "S/N"},
            "paciente": {"nombre_completo": r[10]},
            "pago": {
                "estatus": estatus_del_pago, # <--- Enviará "Pagado" o "Pendiente" al Frontend
                "monto": float(r[7])
            }
        }
        return jsonify(datos)
        
    except Exception as e:
        return jsonify({"error": f"Error interno en la base de datos: {str(e)}"}), 500


@paciente_bp.route("/api/citas/<int:id_cita>/reembolso")
@login_requerido
def api_reembolso_calculo(id_cita):
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.Fecha_cita, c.hora_cita, esp.Costo_Consulta
            FROM CITA c
            JOIN DOCTOR d ON c.Id_doctor = d.Id_doctor
            JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
            WHERE c.Id_cita = ?
        """, id_cita)
        row = cursor.fetchone()

    if not row:
        return jsonify({"error": "No se encontraron registros"}), 404

    # Calcular diferencia horaria entre el momento actual y la cita
    fecha_cita = datetime.combine(row[0], datetime.strptime(str(row[1])[:5], "%H:%M").time())
    horas_restantes = int((fecha_cita - datetime.now()).total_seconds() / 3600)
    costo = float(row[2])

    if horas_restantes >= 48:
        pct, desc = 100, "Cancelación con más de 48 hrs de anticipación"
    elif 24 <= horas_restantes < 48:
        pct, desc = 50, "Cancelación entre 24 y 48 hrs de anticipación"
    else:
        pct, desc = 0, "Cancelación con menos de 24 hrs de anticipación"

    monto_reembolso = (costo * pct) / 100
    penalizacion = costo - monto_reembolso

    return jsonify({
        "horas_restantes": max(0, horas_restantes),
        "descripcion": desc,
        "porcentaje": pct,
        "costo_original": costo,
        "penalizacion": penalizacion,
        "monto_reembolso": monto_reembolso,
        "estatus_pago": "Pendiente"
    })


@paciente_bp.route("/api/citas/<int:id_cita>/cancelar", methods=["POST"])
@login_requerido
def api_cancelar_procesar(id_cita):
    # Obtener desglose de reembolso para reflejar en la respuesta final de éxito
    reem_datos = api_reembolso_calculo(id_cita).get_json()
    
    with get_coneccion() as conn:
        cursor = conn.cursor()
        # Modificar estatus a 0 (Cancelado)
        cursor.execute("UPDATE CITA SET Estatus = 0 WHERE Id_cita = ?", id_cita)
        conn.commit()

    return jsonify({
        "monto_reembolso": reem_datos.get("monto_reembolso"),
        "porcentaje": reem_datos.get("porcentaje"),
        "status": "success"
    })

@paciente_bp.route("/api/citas/<int:id_cita>/pagar", methods=["POST"])
@login_requerido
def api_pagar_cita(id_cita):
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            
            # 1. Verificamos si ya está pagada para evitar pagos dobles
            cursor.execute("SELECT Id_pago FROM PAGO WHERE Id_cita = ?", id_cita)
            if cursor.fetchone():
                return jsonify({"mensaje": "La cita ya se encuentra pagada"}), 200

            # 2. Obtenemos el costo de la consulta
            cursor.execute("""
                SELECT esp.Costo_Consulta 
                FROM CITA c
                JOIN DOCTOR d ON c.Id_doctor = d.Id_doctor
                JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
                WHERE c.Id_cita = ?
            """, id_cita)
            row = cursor.fetchone()
            monto = float(row[0]) if row else 0.0

            # 3. Insertamos el registro. OJO: Mandamos 1 al campo Estatus (BIT)
            cursor.execute("""
                INSERT INTO PAGO (Fecha_pago, Monto, Linea_pago, Estatus, Id_cita)
                VALUES (GETDATE(), ?, 'PAGO-ONLINE', 1, ?)
            """, (monto, id_cita))
            
            conn.commit()
            
        return jsonify({"status": "success", "mensaje": "Pago registrado en BD"})
    except Exception as e:
        return jsonify({"error": f"Error al registrar pago: {str(e)}"}), 500