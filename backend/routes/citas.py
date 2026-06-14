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
    """
    Calcula el % de reembolso según la política de cancelación:
      - 48h+ de anticipación  → 100%
      - 24h–48h               →  50%
      - menos de 24h          →   0%
    Devuelve: { porcentaje, horas_restantes, descripcion }
    """
    hora = td_to_time(hora_cita)
    cita_dt   = datetime.strptime(fecha_cita, "%Y-%m-%d")
    cita_dt   = cita_dt.replace(hour=hora.hour, minute=hora.minute)
    ahora     = datetime.now()
    diferencia = (cita_dt - ahora).total_seconds() / 3600  # en horas

    if diferencia >= 48:
        return {"porcentaje": 100, "horas_restantes": diferencia, "descripcion": "Devolución del 100%"}
    elif diferencia >= 24:
        return {"porcentaje": 50,  "horas_restantes": diferencia, "descripcion": "Devolución del 50%"}
    else:
        return {"porcentaje": 0,   "horas_restantes": diferencia, "descripcion": "Sin devolución (menos de 24h)"}


def get_id_paciente_desde_sesion(cursor):
    """Obtiene el Id_paciente del usuario en sesión."""
    cursor.execute(
        "SELECT Id_paciente FROM PACIENTE WHERE Id_usuario = ?",
        session.get("usuario_id")
    )
    row = cursor.fetchone()
    return row[0] if row else None


# ── Páginas HTML ──────────────────────────────────────────────────────────────

@citas_bp.route("/")
@login_required
@role_required(["Paciente"])
def pagina_citas():
    return render_template("paciente/citasPaciente.html")


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
                SELECT
                    e.Id_especialidad,
                    e.Nombre,
                    e.Descripcion,
                    e.Costo_Consulta,
                    COUNT(d.Id_doctor) AS total_doctores
                FROM ESPECIALIDAD e
                LEFT JOIN DOCTOR d ON d.Id_especialidad = e.Id_especialidad
                GROUP BY e.Id_especialidad, e.Nombre, e.Descripcion, e.Costo_Consulta
                ORDER BY e.Nombre
                """)
            rows = cursor.fetchall()

        return jsonify([{
            "id_especialidad": r[0],
            "nombre":          r[1],
            "descripcion":     r[2],
            "costo_consulta":  float(r[3]) if r[3] else 0.0,
            "total_doctores":  r[4]
        } for r in rows]), 200

    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500


@citas_bp.route("/doctores/<int:id_especialidad>", methods=["GET"])
@login_required
@role_required(["Paciente"])
def get_doctores(id_especialidad):
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            # Modificamos los JOINs para pasar por EMPLEADO_HORARIO (eh)
            cursor.execute("""
                SELECT
                    d.Id_doctor,
                    emp.Nombre,
                    emp.Apellido_Paterno,
                    emp.Apellido_Materno,
                    esp.Nombre          AS especialidad,
                    esp.Costo_Consulta,
                    h.Dia,
                    h.Hora_Inicio,
                    h.Hora_Fin,
                    con.Id_consultorio,
                    con.Numero          AS consultorio_num,
                    con.Piso
                FROM DOCTOR d
                JOIN EMPLEADO        emp ON emp.Id_empleado     = d.Id_empleado
                JOIN ESPECIALIDAD    esp ON esp.Id_especialidad = d.Id_especialidad
                JOIN EMPLEADO_HORARIO eh ON emp.Id_empleado     = eh.Id_empleado
                JOIN HORARIO          h   ON h.Id_Horario       = eh.Id_Horario
                LEFT JOIN CONSULTORIO con ON con.Id_Doctor      = d.Id_doctor
                WHERE d.Id_especialidad = ?
                ORDER BY emp.Apellido_Paterno
            """, id_especialidad)
            rows = cursor.fetchall()

        # Agrupamos en un diccionario usando el Id_doctor como clave
        doctores_dict = {}
        for r in rows:
            id_doc = r[0]
            dia_texto = r[6].strip().lower() if r[6] else ""
            
            if id_doc not in doctores_dict:
                doctores_dict[id_doc] = {
                    "id_doctor":          id_doc,
                    "nombre_completo":    f"Dr. {r[1]} {r[2]} {r[3] or ''}".strip(),
                    "especialidad":       r[4],
                    "costo_consulta":     float(r[5]) if r[5] else 0.0,
                    "dias_trabajo":       [dia_texto] if dia_texto else [], # Lista de días
                    "hora_inicio":        str(td_to_time(r[7])),
                    "hora_fin":           str(td_to_time(r[8])),
                    "id_consultorio":     r[9],
                    "consultorio_numero": r[10],
                    "piso":               r[11],
                }
            else:
                # Si el doctor ya existe, solo añadimos el nuevo día a su lista
                if dia_texto and dia_texto not in doctores_dict[id_doc]["dias_trabajo"]:
                    doctores_dict[id_doc]["dias_trabajo"].append(dia_texto)

        # Retornamos la lista de doctores únicos con sus días agrupados
        return jsonify(list(doctores_dict.values())), 200

    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500


@citas_bp.route("/horas-disponibles", methods=["GET"])
@login_required
@role_required(["Paciente"])
def get_horas_disponibles():
    id_doctor = request.args.get("id_doctor", type=int)
    fecha     = request.args.get("fecha")

    if not id_doctor or not fecha:
        return jsonify({"error": "Se requieren id_doctor y fecha"}), 400

    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()

            # 1. Modificamos la consulta para obtener TODOS los horarios del doctor
            cursor.execute("""
                SELECT h.Hora_Inicio, h.Hora_Fin, h.Dia
                FROM DOCTOR d
                JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
                JOIN EMPLEADO_HORARIO eh ON e.Id_empleado = eh.Id_empleado
                JOIN HORARIO h ON eh.Id_Horario = h.Id_Horario
                WHERE d.Id_doctor = ?
            """, id_doctor)
            horarios_db = cursor.fetchall()

            if not horarios_db:
                return jsonify({"error": "Doctor no encontrado o sin horario asignado"}), 404

            dias_es    = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
            fecha_dt   = datetime.strptime(fecha, "%Y-%m-%d")
            dia_semana = dias_es[fecha_dt.weekday()].lower()

            # 2. Buscar si el doctor atiende en el día específico que el usuario seleccionó
            horario_del_dia = None
            dias_que_atiende = []

            for row in horarios_db:
                dia_db = row[2].strip().lower()
                dias_que_atiende.append(dia_db.capitalize())
                
                # Manejamos el acento en "miércoles" por seguridad
                if dia_db == dia_semana or (dia_semana == "miércoles" and dia_db == "miercoles"):
                    horario_del_dia = row
                    break

            # Si por alguna razón el usuario logra hacer clic en un día que el doc no trabaja
            if not horario_del_dia:
                dias_unicos = ", ".join(sorted(set(dias_que_atiende)))
                return jsonify({
                    "slots": [],
                    "mensaje": f"El doctor solo atiende los días: {dias_unicos}"
                }), 200

            # 3. Si el día es correcto, buscamos qué horas ya están ocupadas
            cursor.execute("""
                SELECT hora_cita, Hora_Fin
                FROM CITA
                WHERE Id_doctor = ? AND Fecha_cita = ? AND Estatus = 1
            """, id_doctor, fecha)
            ocupadas = cursor.fetchall()

        # 4. Calcular los bloques de media hora (slots)
        from datetime import time as dt_time
        # Usamos las horas específicas de ESE día
        inicio = td_to_time(horario_del_dia[0])
        fin    = td_to_time(horario_del_dia[1])

        ocupados = [(td_to_time(c[0]), td_to_time(c[1]) if c[1] else None) for c in ocupadas]

        slots        = []
        cursor_time  = datetime.combine(fecha_dt, inicio)
        fin_dt       = datetime.combine(fecha_dt, fin)
        duracion     = timedelta(minutes=30)

        while cursor_time + duracion <= fin_dt:
            slot_ini = cursor_time.time()
            slot_fin = (cursor_time + duracion).time()

            traslape = any(
                slot_ini < (oc_fin or (datetime.combine(fecha_dt, oc_ini) + duracion).time())
                and slot_fin > oc_ini
                for oc_ini, oc_fin in ocupados
            )

            slots.append({
                "hora":       slot_ini.strftime("%H:%M"),
                "hora_fin":   slot_fin.strftime("%H:%M"),
                "disponible": not traslape
            })
            cursor_time += duracion

        return jsonify({"fecha": fecha, "slots": slots}), 200

    except (pyodbc.Error, ValueError) as e:
        return jsonify({"error": str(e)}), 500


# ── API: Agendar cita ─────────────────────────────────────────────────────────

@citas_bp.route("/agendar", methods=["POST"])
@login_required
@role_required(["Paciente"])
def agendar_cita():
    data      = request.json
    id_doctor = data.get("id_doctor")
    fecha     = data.get("fecha")
    hora      = data.get("hora")

    if not all([id_doctor, fecha, hora]):
        return jsonify({"error": "id_doctor, fecha y hora son obligatorios"}), 400

    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()

            id_paciente = get_id_paciente_desde_sesion(cursor)
            if not id_paciente:
                return jsonify({"error": "Paciente no encontrado"}), 404

            # Consultorio del doctor
            cursor.execute(
                "SELECT Id_consultorio FROM CONSULTORIO WHERE Id_Doctor = ?", id_doctor
            )
            con = cursor.fetchone()
            if not con:
                return jsonify({"error": "El doctor no tiene consultorio asignado"}), 400
            id_consultorio = con[0]

            hora_fin = (datetime.strptime(hora, "%H:%M") + timedelta(minutes=30)).strftime("%H:%M")

            # Validar traslape server-side
            cursor.execute("""
                SELECT COUNT(*) FROM CITA
                WHERE Id_doctor = ? AND Fecha_cita = ? AND Estatus = 1
                  AND hora_cita < ? AND Hora_Fin > ?
            """, id_doctor, fecha, hora_fin, hora)
            if cursor.fetchone()[0] > 0:
                return jsonify({"error": "El horario ya no está disponible. Elige otro."}), 409

            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")

            cursor.execute("""
                EXEC sp_CrearCita
                    @Id_paciente    = ?,
                    @Id_doctor      = ?,
                    @Id_consultorio = ?,
                    @Fecha_cita     = ?,
                    @Hora_cita      = ?,
                    @Hora_Fin       = ?
            """, id_paciente, id_doctor, id_consultorio, fecha, hora, hora_fin)

            conn.commit()

            cursor.execute("SELECT @@IDENTITY")
            id_cita = int(cursor.fetchone()[0])

        return jsonify({
            "mensaje": "Cita agendada exitosamente",
            "id_cita": id_cita,
            "fecha":   fecha,
            "hora":    hora,
            "hora_fin": hora_fin
        }), 201

    except pyodbc.Error as e:
        # El mensaje del RAISERROR viene en e.args[1]
        msg = str(e.args[1]) if len(e.args) > 1 else str(e)
        # Limpiar el prefijo que agrega SQL Server
        match = re.search(r"\[SQL Server\](.*?)(\(|$)", msg)
        error_limpio = match.group(1).strip() if match else msg
        return jsonify({"error": error_limpio}), 400


# ── API: Mis citas (lista para citasPaciente.html) ────────────────────────────

@citas_bp.route("/mis-citas", methods=["GET"])
@login_required
@role_required(["Paciente"])
def mis_citas():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()

            id_paciente = get_id_paciente_desde_sesion(cursor)
            if not id_paciente:
                return jsonify({"error": "Paciente no encontrado"}), 404

            cursor.execute("""
                SELECT
                    v.Id_cita,
                    v.Paciente,
                    v.Fecha_cita,
                    v.hora_cita,
                    v.Estatus,
                    v.Doctor,
                    v.Especialidad,
                    v.Consultorio,
                    v.Piso
                FROM VW_Detalle_Cita_Paciente v
                WHERE v.Id_cita IN (
                    SELECT Id_cita FROM CITA WHERE Id_paciente = ?
                )
                ORDER BY v.Fecha_cita DESC
            """, id_paciente)
            rows = cursor.fetchall()

        citas = [{
            "id_cita":          r[0],
            "fecha":            str(r[1]),
            "hora_inicio":      str(td_to_time(r[2])),
            "hora_fin":         str(td_to_time(r[3])) if r[3] else None,
            "estatus":          "Activa" if r[4] else "Cancelada",
            "doctor":           f"Dr. {r[5]} {r[6]}",
            "especialidad":     r[7],
            "consultorio":      f"Consultorio {r[8]}, Piso {r[9]}",
            "estatus_pago":     r[10],
            "folio":            f"RASA-{str(r[0]).zfill(6)}"
        } for r in rows]

        return jsonify(citas), 200

    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500


# ── API: Detalle de una cita (detallesCita.html y comprobanteCita.html) ─────────

@citas_bp.route("/<int:id_cita>", methods=["GET"])
@login_required
@role_required(["Paciente", "Recepcionista"])
def detalle_cita(id_cita):
    try:
        with get_coneccion() as conn:
            # 1. PRIMERO creamos el cursor
            cursor = conn.cursor()
            # 2. LUEGO lo usamos para obtener el paciente
            id_paciente = get_id_paciente_desde_sesion(cursor)

            # 3. Consulta ajustada para traer todo lo que requiere el comprobante
            cursor.execute("""
                SELECT
                    c.Id_cita,
                    c.Fecha_cita,
                    c.hora_cita,
                    c.Hora_Fin,
                    c.Estatus,
                    p.Nombre + ' ' + p.Apellido_Paterno AS paciente_nombre,
                    e.Nombre + ' ' + e.Apellido_Paterno AS doctor_nombre,
                    esp.Nombre AS especialidad,
                    esp.Costo_Consulta,
                    con.Numero AS consultorio_num,
                    con.Piso,
                    ISNULL((SELECT TOP 1 Estatus_pago FROM TICKET t WHERE t.Id_cita = c.Id_cita), 'Pendiente') AS pago_estatus
                FROM CITA c
                JOIN PACIENTE p ON c.Id_paciente = p.Id_paciente
                JOIN DOCTOR d ON c.Id_doctor = d.Id_doctor
                JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
                JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
                LEFT JOIN CONSULTORIO con ON c.Id_consultorio = con.Id_consultorio
                WHERE c.Id_cita = ? AND c.Id_paciente = ?
            """, (id_cita, id_paciente))
            
            r = cursor.fetchone()

        if not r:
            return jsonify({"error": "Cita no encontrada"}), 404

        # Limpiamos las horas para quitar los segundos (ej. "13:00")
        hora_ini_str = str(td_to_time(r[2]))[:5] if r[2] else "00:00"
        hora_fin_str = str(td_to_time(r[3]))[:5] if r[3] else "00:00"

        # 4. Armamos el diccionario EXACTO que esperan tus archivos HTML
        datos = {
            "id_cita": r[0],
            "folio": f"CIT-{str(r[0]).zfill(4)}",
            "estatus": "Activa" if r[4] == 1 else "Cancelada",
            "fecha": str(r[1]),             # Para detallesCita.html
            "hora_inicio": hora_ini_str,    # Para detallesCita.html
            "hora_fin": hora_fin_str,       # Para detallesCita.html
            "cita": {                       # Para comprobanteCita.html
                "fecha": str(r[1]),
                "hora_inicio": hora_ini_str,
                "hora_fin": hora_fin_str
            },
            "paciente": {
                "nombre_completo": r[5].strip()
            },
            "doctor": {
                "nombre_completo": f"Dr. {r[6].strip()}",
                "especialidad": r[7],
                "costo_consulta": float(r[8]) if r[8] else 0.0
            },
            "consultorio": {
                "numero": r[9] if r[9] else "S/N",
                "piso": r[10] if r[10] else "PB"
            },
            "pago": {
                "estatus": r[11],
                "monto": float(r[8]) if r[8] else 0.0
            }
        }

        return jsonify(datos), 200

    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500


# ── API: Comprobante completo (comprobanteCita.html) ──────────────────────────

@citas_bp.route("/comprobante/<int:id_cita>/datos", methods=["GET"])
@login_required
@role_required(["Paciente"])
def datos_comprobante(id_cita):
    """Endpoint JSON que llama el frontend al cargar comprobanteCita.html."""
    # Reutiliza la misma query que detalle_cita pero agrega código de barras y fecha generación
    resp = detalle_cita(id_cita)
    if resp[1] != 200:
        return resp

    data = resp[0].get_json()
    data["fecha_generacion"] = datetime.now().strftime("%d de %B, %Y a las %I:%M %p")
    data["codigo_barras"]    = f"*RASA{str(id_cita).zfill(8)}*"

    return jsonify(data), 200


# ── API: Calcular reembolso antes de cancelar ─────────────────────────────────

@citas_bp.route("/<int:id_cita>/reembolso", methods=["GET"])
@login_required
@role_required(["Paciente", "Recepcionista"])
def calcular_reembolso(id_cita):
    """Devuelve el desglose del reembolso para mostrar en cancelarCita.html."""
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    c.Fecha_cita,
                    c.hora_cita,
                    c.Estatus,
                    esp.Costo_Consulta,
                    ISNULL(
                        (SELECT TOP 1 Estatus_pago
                         FROM TICKET t WHERE t.Id_cita = c.Id_cita), 'Pendiente'
                    ) AS estatus_pago,
                    ISNULL(
                        (SELECT TOP 1 Monto_total
                         FROM TICKET t WHERE t.Id_cita = c.Id_cita), 0
                    ) AS monto_pagado
                FROM CITA c
                JOIN DOCTOR       d   ON d.Id_doctor        = c.Id_doctor
                JOIN ESPECIALIDAD esp ON esp.Id_especialidad = d.Id_especialidad
                WHERE c.Id_cita = ?
            """, id_cita)
            r = cursor.fetchone()

        if not r:
            return jsonify({"error": "Cita no encontrada"}), 404

        if not r[2]:  # Estatus = 0 = ya cancelada
            return jsonify({"error": "La cita ya está cancelada"}), 400

        reembolso  = calcular_porcentaje_reembolso(str(r[0]), r[1])
        costo      = float(r[5]) if r[5] else float(r[3]) if r[3] else 0.0
        monto_dev  = round(costo * reembolso["porcentaje"] / 100, 2)
        penalizacion = round(costo - monto_dev, 2)

        return jsonify({
            "id_cita":          id_cita,
            "costo_original":   costo,
            "porcentaje":       reembolso["porcentaje"],
            "penalizacion":     penalizacion,
            "monto_reembolso":  monto_dev,
            "horas_restantes":  round(reembolso["horas_restantes"], 1),
            "descripcion":      reembolso["descripcion"],
            "estatus_pago":     r[4]
        }), 200

    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500


# ── API: Cancelar cita ────────────────────────────────────────────────────────

@citas_bp.route("/<int:id_cita>/cancelar", methods=["POST"])
@login_required
@role_required(["Paciente", "Recepcionista"])
def cancelar_cita(id_cita):
    """
    Cancela la cita, registra en BITACORA_CITA y calcula el reembolso.
    Body JSON opcional: { "motivo": "..." }
    """
    motivo = (request.json or {}).get("motivo", "")
    rol    = session.get("rol")

    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()

            # Verificar que la cita existe y está activa
            cursor.execute("""
                SELECT c.Estatus, c.Fecha_cita, c.hora_cita, c.Hora_Fin,
                       c.Id_paciente, esp.Costo_Consulta
                FROM CITA c
                JOIN DOCTOR       d   ON d.Id_doctor        = c.Id_doctor
                JOIN ESPECIALIDAD esp ON esp.Id_especialidad = d.Id_especialidad
                WHERE c.Id_cita = ?
            """, id_cita)
            cita = cursor.fetchone()

            if not cita:
                return jsonify({"error": "Cita no encontrada"}), 404
            if not cita[0]:
                return jsonify({"error": "La cita ya está cancelada"}), 400

            # Si es paciente, verificar que la cita le pertenece
            if rol == "Paciente":
                id_paciente = get_id_paciente_desde_sesion(cursor)
                if cita[4] != id_paciente:
                    return jsonify({"error": "No tienes permiso para cancelar esta cita"}), 403

            # Calcular reembolso
            reembolso    = calcular_porcentaje_reembolso(str(cita[1]), cita[2])
            costo        = float(cita[5]) if cita[5] else 0.0
            monto_dev    = round(costo * reembolso["porcentaje"] / 100, 2)

            # Marcar cita como cancelada
            cursor.execute(
                "UPDATE CITA SET Estatus = 0 WHERE Id_cita = ?", id_cita
            )

            # Registrar en BITACORA_CITA
            # Id_Recepcionista: si cancela un paciente ponemos NULL-safe buscando
            # el recepcionista de turno; por ahora usamos 1 como placeholder
            # hasta que implementes la selección de recepcionista activo
            id_recep = 1
            if rol == "Recepcionista":
                cursor.execute("""
                    SELECT r.Id_Recepcionista
                    FROM RECEPCIONISTA r
                    JOIN EMPLEADO e ON e.Id_empleado = r.Id_empleado
                    WHERE e.Id_usuario = ?
                """, session.get("usuario_id"))
                rec = cursor.fetchone()
                if rec:
                    id_recep = rec[0]

            hora_ini = td_to_time(cita[2])
            hora_fin = td_to_time(cita[3]) if cita[3] else hora_ini

            cursor.execute("""
                INSERT INTO BITACORA_CITA (
                    Id_cita, Id_Recepcionista, Estatus_cita,
                    Monto_devuelto, Inicio, Fin
                ) VALUES (?, ?, 0, ?, ?, ?)
            """, id_cita, id_recep, monto_dev,
                hora_ini.strftime("%H:%M"),
                hora_fin.strftime("%H:%M"))

            conn.commit()

        return jsonify({
            "mensaje":         "Cita cancelada exitosamente",
            "id_cita":         id_cita,
            "monto_reembolso": monto_dev,
            "porcentaje":      reembolso["porcentaje"],
            "descripcion":     reembolso["descripcion"]
        }), 200

    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500