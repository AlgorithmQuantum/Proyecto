from flask import Blueprint, request, jsonify, session, render_template, redirect
from middleware.auth import login_required, role_required
from database.db import get_coneccion
from datetime import datetime, timedelta
import pyodbc
import re

citas_bp = Blueprint("citas", __name__, url_prefix="/citas")

# ── Helpers ───────────────────────────────────────────────────────────────────

def td_to_time(val):
    """Convierte timedelta (que devuelve pyodbc) a objeto time."""
    if isinstance(val, timedelta):
        total = int(val.total_seconds())
        from datetime import time as dt_time
        return dt_time(total // 3600, (total % 3600) // 60)
    return val

def calcular_porcentaje_reembolso(fecha_cita: str, hora_cita) -> dict:
    """Calcula el % de reembolso según la política de cancelación"""
    hora = td_to_time(hora_cita)
    cita_dt   = datetime.strptime(fecha_cita, "%Y-%m-%d")
    cita_dt   = cita_dt.replace(hour=hora.hour, minute=hora.minute)
    ahora     = datetime.now()
    diferencia = (cita_dt - ahora).total_seconds() / 3600  

    if diferencia >= 48:
        return {"porcentaje": 100, "horas_restantes": diferencia, "descripcion": "Devolución del 100%"}
    elif diferencia >= 24:
        return {"porcentaje": 50,  "horas_restantes": diferencia, "descripcion": "Devolución del 50%"}
    else:
        return {"porcentaje": 0,   "horas_restantes": diferencia, "descripcion": "Sin devolución (menos de 24h)"}

def get_id_paciente_desde_sesion(cursor=None):
    """Obtiene el Id_paciente correcto de la sesión."""
    # CORRECCIÓN: Unificado con auth.py y paciente.py
    return session.get("id_entidad")

# ── Páginas HTML ──────────────────────────────────────────────────────────────

@citas_bp.route("/")
@login_required
@role_required(["Paciente"])
def pagina_citas():
    tiene_pendiente = False
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            id_paciente = get_id_paciente_desde_sesion()
            
            if id_paciente:
                cursor.execute("""
                    SELECT 1 FROM CITA 
                    WHERE Id_paciente = ? AND Estatus = 1 AND Id_receta IS NULL
                """, id_paciente)
                
                if cursor.fetchone():
                    tiene_pendiente = True
    except Exception as e:
        print("Error al verificar citas pendientes:", e)
        pass

    return render_template("paciente/citasPaciente.html", tiene_pendiente=tiene_pendiente)

@citas_bp.route("/agendar/pagina")
@login_required
@role_required(["Paciente"])
def pagina_agendar():
    return render_template("paciente/agendarCita.html")

@citas_bp.route("/comprobante/<int:id_cita>")
@login_required
@role_required(["Paciente"])
def pagina_comprobante(id_cita):
    return render_template("paciente/comprobanteCita.html", id_cita=id_cita)

@citas_bp.route("/detalles/<int:id_cita>")
@login_required
@role_required(["Paciente"])
def pagina_detalles(id_cita):
    return render_template("paciente/detallesCita.html", id_cita=id_cita)

@citas_bp.route("/cancelar/<int:id_cita>")
@login_required
@role_required(["Paciente", "Recepcionista"])
def pagina_cancelar(id_cita):
    return render_template("paciente/cancelarCita.html", id_cita=id_cita)

# ── API: Catálogos ────────────────────────────────────────────────────────────

@citas_bp.route("/especialidades", methods=["GET"])
@login_required
@role_required(["Paciente"])
def get_especialidades():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.Id_especialidad, e.Nombre, e.Descripcion, e.Costo_Consulta, COUNT(d.Id_doctor) AS total_doctores
                FROM ESPECIALIDAD e
                LEFT JOIN DOCTOR d ON d.Id_especialidad = e.Id_especialidad
                GROUP BY e.Id_especialidad, e.Nombre, e.Descripcion, e.Costo_Consulta
                ORDER BY e.Nombre
                """)
            rows = cursor.fetchall()
        return jsonify([{"id_especialidad": r[0], "nombre": r[1], "descripcion": r[2], "costo_consulta": float(r[3]) if r[3] else 0.0, "total_doctores": r[4]} for r in rows]), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500

@citas_bp.route("/doctores/<int:id_especialidad>", methods=["GET"])
@login_required
@role_required(["Paciente"])
def get_doctores(id_especialidad):
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.Id_doctor, emp.Nombre, emp.Apellido_Paterno, emp.Apellido_Materno,
                       esp.Nombre AS especialidad, esp.Costo_Consulta, h.Dia, h.Hora_Inicio, h.Hora_Fin,
                       con.Id_consultorio, con.Numero AS consultorio_num, con.Piso
                FROM DOCTOR d
                JOIN EMPLEADO emp ON emp.Id_empleado = d.Id_empleado
                JOIN ESPECIALIDAD esp ON esp.Id_especialidad = d.Id_especialidad
                JOIN EMPLEADO_HORARIO eh ON emp.Id_empleado = eh.Id_empleado
                JOIN HORARIO h ON h.Id_Horario = eh.Id_Horario
                LEFT JOIN CONSULTORIO con ON con.Id_Doctor = d.Id_doctor
                WHERE d.Id_especialidad = ?
                ORDER BY emp.Apellido_Paterno
            """, id_especialidad)
            rows = cursor.fetchall()

        doctores_dict = {}
        for r in rows:
            id_doc = r[0]
            dia_texto = r[6].strip().lower() if r[6] else ""
            if id_doc not in doctores_dict:
                doctores_dict[id_doc] = {
                    "id_doctor": id_doc, "nombre_completo": f"Dr. {r[1]} {r[2]} {r[3] or ''}".strip(),
                    "especialidad": r[4], "costo_consulta": float(r[5]) if r[5] else 0.0,
                    "dias_trabajo": [dia_texto] if dia_texto else [], "hora_inicio": str(td_to_time(r[7])),
                    "hora_fin": str(td_to_time(r[8])), "id_consultorio": r[9], "consultorio_numero": r[10], "piso": r[11],
                }
            else:
                if dia_texto and dia_texto not in doctores_dict[id_doc]["dias_trabajo"]:
                    doctores_dict[id_doc]["dias_trabajo"].append(dia_texto)
        return jsonify(list(doctores_dict.values())), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500

@citas_bp.route("/horas-disponibles", methods=["GET"])
@login_required
@role_required(["Paciente"])
def get_horas_disponibles():
    id_doctor = request.args.get("id_doctor", type=int)
    fecha = request.args.get("fecha")
    if not id_doctor or not fecha: return jsonify({"error": "Se requieren id_doctor y fecha"}), 400
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT h.Hora_Inicio, h.Hora_Fin, h.Dia
                FROM DOCTOR d JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
                JOIN EMPLEADO_HORARIO eh ON e.Id_empleado = eh.Id_empleado
                JOIN HORARIO h ON eh.Id_Horario = h.Id_Horario
                WHERE d.Id_doctor = ?
            """, id_doctor)
            horarios_db = cursor.fetchall()

            if not horarios_db: return jsonify({"error": "Doctor no encontrado o sin horario asignado"}), 404

            dias_es = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            dia_semana = dias_es[fecha_dt.weekday()].lower()

            horario_del_dia = next((row for row in horarios_db if row[2].strip().lower() == dia_semana or (dia_semana == "miércoles" and row[2].strip().lower() == "miercoles")), None)
            if not horario_del_dia: return jsonify({"slots": [], "mensaje": "El doctor no atiende en el día seleccionado."}), 200

            cursor.execute("SELECT hora_cita, Hora_Fin FROM CITA WHERE Id_doctor = ? AND Fecha_cita = ? AND Estatus = 1", id_doctor, fecha)
            ocupadas = cursor.fetchall()

        inicio, fin = td_to_time(horario_del_dia[0]), td_to_time(horario_del_dia[1])
        ocupados = [(td_to_time(c[0]), td_to_time(c[1]) if c[1] else None) for c in ocupadas]
        slots, cursor_time, fin_dt, duracion = [], datetime.combine(fecha_dt, inicio), datetime.combine(fecha_dt, fin), timedelta(minutes=30)
        limite_estricto_48h = datetime.now() + timedelta(hours=48)

        while cursor_time + duracion <= fin_dt:
            slot_ini, slot_fin = cursor_time.time(), (cursor_time + duracion).time()
            traslape_cita = any(slot_ini < (oc_fin or (datetime.combine(fecha_dt, oc_ini) + duracion).time()) and slot_fin > oc_ini for oc_ini, oc_fin in ocupados)
            slots.append({"hora": slot_ini.strftime("%H:%M"), "hora_fin": slot_fin.strftime("%H:%M"), "disponible": (not traslape_cita) and (cursor_time >= limite_estricto_48h)})
            cursor_time += duracion

        return jsonify({"fecha": fecha, "slots": slots}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── API: Agendar cita ─────────────────────────────────────────────────────────

@citas_bp.route("/agendar", methods=["POST"])
@login_required
@role_required(["Paciente"])
def agendar_cita():
    data = request.json
    id_doctor, fecha, hora = data.get("id_doctor"), data.get("fecha"), data.get("hora")
    if not all([id_doctor, fecha, hora]): return jsonify({"error": "id_doctor, fecha y hora son obligatorios"}), 400
    
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            id_paciente = get_id_paciente_desde_sesion()
            if not id_paciente: return jsonify({"error": "Paciente no encontrado"}), 404

            cursor.execute("SELECT 1 FROM CITA WHERE Id_paciente = ? AND Estatus = 1 AND Id_receta IS NULL", id_paciente)
            if cursor.fetchone(): return jsonify({"error": "Ya tienes una cita agendada pendiente."}), 409
            
            cursor.execute("SELECT TOP 1 Id_consultorio FROM CONSULTORIO WHERE Id_Doctor = ?", id_doctor)
            con = cursor.fetchone()
            if not con: return jsonify({"error": "El doctor no tiene consultorio asignado"}), 400
            
            hora_fin = (datetime.strptime(hora, "%H:%M") + timedelta(minutes=30)).strftime("%H:%M")
            cursor.execute("SELECT COUNT(*) FROM CITA WHERE Id_doctor = ? AND Fecha_cita = ? AND Estatus = 1 AND hora_cita < ? AND Hora_Fin > ?", id_doctor, fecha, hora_fin, hora)
            if cursor.fetchone()[0] > 0: return jsonify({"error": "El horario ya no está disponible."}), 409

            cursor.execute("""
                EXEC sp_CrearCita @Id_paciente=?, @Id_doctor=?, @Id_consultorio=?, @Fecha_cita=?, @Hora_cita=?, @Hora_Fin=?
            """, id_paciente, id_doctor, con[0], fecha, hora, hora_fin)
            
            # CORRECCIÓN: Método más exacto para obtener el ID de la cita recién creada
            cursor.execute("SELECT IDENT_CURRENT('CITA')")
            row_id = cursor.fetchone()
            id_cita = int(row_id[0]) if row_id and row_id[0] else None
            conn.commit()

        return jsonify({"mensaje": "Cita agendada exitosamente", "id_cita": id_cita, "fecha": fecha, "hora": hora, "hora_fin": hora_fin}), 201

    except pyodbc.Error as e:
        msg = str(e.args[1]) if len(e.args) > 1 else str(e)
        match = re.search(r"\[SQL Server\](.*?)(\(|$)", msg)
        return jsonify({"error": match.group(1).strip() if match else msg}), 400

# ── API: Mis citas ────────────────────────────

@citas_bp.route("/mis-citas", methods=["GET"])
@login_required
@role_required(["Paciente"])
def mis_citas():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            id_paciente = get_id_paciente_desde_sesion()
            if not id_paciente: return jsonify({"error": "Paciente no encontrado"}), 404

            cursor.execute("""
                SELECT v.Id_cita, v.Paciente, v.Fecha_cita, v.hora_cita, v.Estatus, v.Doctor, v.Especialidad, v.Consultorio, v.Piso
                FROM VW_Detalle_Cita_Paciente v
                WHERE v.Id_cita IN (SELECT Id_cita FROM CITA WHERE Id_paciente = ?)
                ORDER BY v.Fecha_cita DESC
            """, id_paciente)
            rows = cursor.fetchall()
        return jsonify([{"id_cita": r[0], "fecha": str(r[1]), "hora_inicio": str(td_to_time(r[2])), "hora_fin": str(td_to_time(r[3])) if r[3] else None, "estatus": "Activa" if r[4] else "Cancelada", "doctor": f"Dr. {r[5]} {r[6]}", "especialidad": r[7], "consultorio": f"Consultorio {r[8]}, Piso {r[9]}", "folio": f"RASA-{str(r[0]).zfill(6)}"} for r in rows]), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500

# ── API: Detalle y Comprobante ──────────────────────────────────────────────

@citas_bp.route("/<int:id_cita>", methods=["GET"])
@login_required
@role_required(["Paciente", "Recepcionista"])
def detalle_cita(id_cita):
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            id_paciente = get_id_paciente_desde_sesion()
            cursor.execute("""
                SELECT c.Id_cita, c.Id_paciente, p.Nombre + ' ' + p.Apellido_Paterno AS paciente_nombre, c.Fecha_cita, c.hora_cita, c.Hora_Fin, c.Estatus, d.Id_doctor, e.Nombre + ' ' + e.Apellido_Paterno AS doctor_nombre, esp.Nombre AS especialidad, esp.Costo_Consulta, con.Numero AS consultorio_num, con.Piso, r.Diagnostico, ISNULL((SELECT TOP 1 Estatus_pago FROM TICKET t WHERE t.Id_cita = c.Id_cita), 'Pendiente') AS pago_estatus
                FROM CITA c JOIN PACIENTE p ON c.Id_paciente = p.Id_paciente
                JOIN DOCTOR d ON c.Id_doctor = d.Id_doctor JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
                JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
                LEFT JOIN CONSULTORIO con ON c.Id_consultorio = con.Id_consultorio
                LEFT JOIN RECETA r ON c.Id_receta = r.Id_receta
                WHERE c.Id_cita = ? AND c.Id_paciente = ?
            """, (id_cita, id_paciente))
            r = cursor.fetchone()

        if not r: return jsonify({"error": "Cita no encontrada o no tienes permisos"}), 404

        return jsonify({
            "id_cita": r[0], "folio": f"RASA-{str(r[0]).zfill(6)}",
            "paciente": {"id_paciente": r[1], "nombre_completo": r[2].strip()},
            "cita": {"fecha": str(r[3]), "hora_inicio": str(td_to_time(r[4]))[:5] if r[4] else "00:00", "hora_fin": str(td_to_time(r[5]))[:5] if r[5] else "00:00"},
            "estatus": "Activa" if r[6] == 1 else "Cancelada",
            "doctor": {"id_doctor": r[7], "nombre_completo": f"Dr. {r[8]}", "especialidad": r[9], "costo_consulta": float(r[10]) if r[10] else 0.0},
            "consultorio": {"numero": r[11] if r[11] else "S/N", "piso": r[12] if r[12] else "PB"},
            "diagnostico": r[13], "pago": {"estatus": r[14], "monto": float(r[10]) if r[10] else 0.0}
        }), 200
    except pyodbc.Error as e: return jsonify({"error": str(e)}), 500

@citas_bp.route("/comprobante/<int:id_cita>/datos", methods=["GET"])
@login_required
@role_required(["Paciente"])
def datos_comprobante(id_cita):
    resp = detalle_cita(id_cita)
    if resp[1] != 200: return resp
    data = resp[0].get_json()
    data["fecha_generacion"] = datetime.now().strftime("%d de %B, %Y a las %I:%M %p")
    data["codigo_barras"] = f"*RASA{str(id_cita).zfill(8)}*"
    return jsonify(data), 200

# ── API: Cancelaciones ────────────────────────────────────────────────────────

@citas_bp.route("/<int:id_cita>/reembolso", methods=["GET"])
@login_required
@role_required(["Paciente", "Recepcionista"])
def calcular_reembolso(id_cita):
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.Fecha_cita, c.hora_cita, c.Estatus, esp.Costo_Consulta, ISNULL((SELECT TOP 1 Estatus_pago FROM TICKET t WHERE t.Id_cita = c.Id_cita), 'Pendiente') AS estatus_pago
                FROM CITA c JOIN DOCTOR d ON d.Id_doctor = c.Id_doctor JOIN ESPECIALIDAD esp ON esp.Id_especialidad = d.Id_especialidad
                WHERE c.Id_cita = ?
            """, id_cita)
            r = cursor.fetchone()

        if not r: return jsonify({"error": "Cita no encontrada"}), 404
        if not r[2]: return jsonify({"error": "La cita ya está cancelada"}), 400

        reembolso = calcular_porcentaje_reembolso(str(r[0]), r[1])
        costo = float(r[3]) if r[3] else 0.0
        monto_dev = round(costo * reembolso["porcentaje"] / 100, 2)
        return jsonify({"id_cita": id_cita, "costo_original": costo, "porcentaje": reembolso["porcentaje"], "penalizacion": round(costo - monto_dev, 2), "monto_reembolso": monto_dev, "horas_restantes": round(reembolso["horas_restantes"], 1), "descripcion": reembolso["descripcion"], "estatus_pago": r[4]}), 200
    except pyodbc.Error as e: return jsonify({"error": str(e)}), 500

@citas_bp.route("/<int:id_cita>/cancelar", methods=["POST"])
@login_required
@role_required(["Paciente", "Recepcionista"])
def cancelar_cita(id_cita):
    rol = session.get("rol")
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.Estatus, c.Fecha_cita, c.hora_cita, c.Hora_Fin, c.Id_paciente, esp.Costo_Consulta
                FROM CITA c JOIN DOCTOR d ON d.Id_doctor = c.Id_doctor JOIN ESPECIALIDAD esp ON esp.Id_especialidad = d.Id_especialidad
                WHERE c.Id_cita = ?
            """, id_cita)
            cita = cursor.fetchone()

            if not cita: return jsonify({"error": "Cita no encontrada"}), 404
            if not cita[0]: return jsonify({"error": "La cita ya está cancelada"}), 400
            
            if rol == "Paciente":
                if cita[4] != get_id_paciente_desde_sesion():
                    return jsonify({"error": "No tienes permiso para cancelar esta cita"}), 403

            reembolso = calcular_porcentaje_reembolso(str(cita[1]), cita[2])
            costo = float(cita[5]) if cita[5] else 0.0
            monto_dev = round(costo * reembolso["porcentaje"] / 100, 2)

            cursor.execute("UPDATE CITA SET Estatus = 0 WHERE Id_cita = ?", id_cita)

            id_recep = 1
            if rol == "Recepcionista":
                # CORRECCIÓN: Evita el choque con la sesión "fantasma"
                cursor.execute("""
                    SELECT r.Id_Recepcionista FROM RECEPCIONISTA r
                    JOIN EMPLEADO e ON e.Id_empleado = r.Id_empleado WHERE e.Id_usuario = ?
                """, session.get("id_usuario"))
                rec = cursor.fetchone()
                if rec: id_recep = rec[0]

            hora_ini, hora_fin = td_to_time(cita[2]), td_to_time(cita[3]) if cita[3] else td_to_time(cita[2])
            cursor.execute("""
                INSERT INTO BITACORA_CITA (Id_cita, Id_Recepcionista, Estatus_cita, Monto_devuelto, Inicio, Fin)
                VALUES (?, ?, 0, ?, ?, ?)
            """, id_cita, id_recep, monto_dev, hora_ini.strftime("%H:%M"), hora_fin.strftime("%H:%M"))
            conn.commit()

        return jsonify({"mensaje": "Cita cancelada", "id_cita": id_cita, "monto_reembolso": monto_dev, "porcentaje": reembolso["porcentaje"], "descripcion": reembolso["descripcion"]}), 200
    except pyodbc.Error as e: return jsonify({"error": str(e)}), 500