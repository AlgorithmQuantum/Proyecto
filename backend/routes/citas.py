from flask import Blueprint, request, jsonify, session, render_template, redirect
from middleware.auth import login_required, role_required
from database.db import get_coneccion
from datetime import datetime, timedelta
import pyodbc

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
                HAVING COUNT(d.Id_doctor) > 0
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
                JOIN EMPLEADO     emp ON emp.Id_empleado      = d.Id_empleado
                JOIN ESPECIALIDAD esp ON esp.Id_especialidad  = d.Id_especialidad
                JOIN HORARIO      h   ON h.Id_Horario         = d.Id_Horario
                LEFT JOIN CONSULTORIO con ON con.Id_Doctor    = d.Id_doctor
                WHERE d.Id_especialidad = ?
                ORDER BY emp.Apellido_Paterno
            """, id_especialidad)
            rows = cursor.fetchall()

        return jsonify([{
            "id_doctor":          r[0],
            "nombre_completo":    f"Dr. {r[1]} {r[2]} {r[3] or ''}".strip(),
            "especialidad":       r[4],
            "costo_consulta":     float(r[5]) if r[5] else 0.0,
            "dia_horario":        r[6],
            "hora_inicio":        str(td_to_time(r[7])),
            "hora_fin":           str(td_to_time(r[8])),
            "id_consultorio":     r[9],
            "consultorio_numero": r[10],
            "piso":               r[11],
        } for r in rows]), 200

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

            cursor.execute("""
                SELECT h.Hora_Inicio, h.Hora_Fin, h.Dia
                FROM DOCTOR d
                JOIN HORARIO h ON h.Id_Horario = d.Id_Horario
                WHERE d.Id_doctor = ?
            """, id_doctor)
            horario = cursor.fetchone()

            if not horario:
                return jsonify({"error": "Doctor no encontrado"}), 404

            dias_es    = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
            fecha_dt   = datetime.strptime(fecha, "%Y-%m-%d")
            dia_semana = dias_es[fecha_dt.weekday()]

            if dia_semana.lower() != horario[2].lower():
                return jsonify({
                    "disponibles": [],
                    "mensaje": f"El doctor solo atiende los {horario[2]}"
                }), 200

            cursor.execute("""
                SELECT hora_cita, Hora_Fin
                FROM CITA
                WHERE Id_doctor = ? AND Fecha_cita = ? AND Estatus = 1
            """, id_doctor, fecha)
            ocupadas = cursor.fetchall()

        from datetime import time as dt_time
        inicio = td_to_time(horario[0])
        fin    = td_to_time(horario[1])

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
                INSERT INTO CITA (
                    Id_paciente, Id_doctor, Id_consultorio,
                    Fecha_cita, hora_cita, Hora_Fin,
                    Dia, Mes, Estatus
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, id_paciente, id_doctor, id_consultorio,
                fecha, hora, hora_fin,
                fecha_dt.day, fecha_dt.month)

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
        return jsonify({"error": str(e)}), 500


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
                    c.Id_cita,
                    c.Fecha_cita,
                    c.hora_cita,
                    c.Hora_Fin,
                    c.Estatus,
                    emp.Nombre           AS doc_nombre,
                    emp.Apellido_Paterno AS doc_ap,
                    esp.Nombre           AS especialidad,
                    con.Numero           AS consultorio_num,
                    con.Piso,
                    -- Si existe ticket pagado
                    ISNULL(
                        (SELECT TOP 1 Estatus_pago
                         FROM TICKET t WHERE t.Id_cita = c.Id_cita), 'Sin ticket'
                    ) AS estatus_pago
                FROM CITA c
                JOIN DOCTOR       d   ON d.Id_doctor        = c.Id_doctor
                JOIN EMPLEADO     emp ON emp.Id_empleado     = d.Id_empleado
                JOIN ESPECIALIDAD esp ON esp.Id_especialidad = d.Id_especialidad
                JOIN CONSULTORIO  con ON con.Id_consultorio  = c.Id_consultorio
                WHERE c.Id_paciente = ?
                ORDER BY c.Fecha_cita DESC, c.hora_cita DESC
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


# ── API: Detalle de una cita (detallesCita.html) ──────────────────────────────

@citas_bp.route("/<int:id_cita>", methods=["GET"])
@login_required
@role_required(["Paciente", "Recepcionista"])
def detalle_cita(id_cita):
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    c.Id_cita,
                    c.Fecha_cita,
                    c.hora_cita,
                    c.Hora_Fin,
                    c.Estatus,
                    c.Diagnostico,
                    c.Tratamiento,
                    -- Paciente
                    p.Nombre,
                    p.Apellido_Paterno,
                    p.Apellido_Materno,
                    p.Id_paciente,
                    -- Doctor
                    emp.Nombre           AS doc_nombre,
                    emp.Apellido_Paterno AS doc_ap,
                    emp.Apellido_Materno AS doc_am,
                    esp.Nombre           AS especialidad,
                    esp.Costo_Consulta,
                    -- Consultorio
                    con.Numero,
                    con.Piso,
                    -- Pago
                    ISNULL(
                        (SELECT TOP 1 Estatus_pago
                         FROM TICKET t WHERE t.Id_cita = c.Id_cita), 'Pendiente'
                    ) AS estatus_pago,
                    ISNULL(
                        (SELECT TOP 1 Monto_total
                         FROM TICKET t WHERE t.Id_cita = c.Id_cita), 0
                    ) AS monto_pagado
                FROM CITA c
                JOIN PACIENTE     p   ON p.Id_paciente      = c.Id_paciente
                JOIN DOCTOR       d   ON d.Id_doctor        = c.Id_doctor
                JOIN EMPLEADO     emp ON emp.Id_empleado     = d.Id_empleado
                JOIN ESPECIALIDAD esp ON esp.Id_especialidad = d.Id_especialidad
                JOIN CONSULTORIO  con ON con.Id_consultorio  = c.Id_consultorio
                WHERE c.Id_cita = ?
            """, id_cita)
            r = cursor.fetchone()

        if not r:
            return jsonify({"error": "Cita no encontrada"}), 404

        return jsonify({
            "folio":         f"RASA-{str(r[0]).zfill(6)}",
            "id_cita":       r[0],
            "fecha":         str(r[1]),
            "hora_inicio":   str(td_to_time(r[2])),
            "hora_fin":      str(td_to_time(r[3])) if r[3] else None,
            "estatus":       "Activa" if r[4] else "Cancelada",
            "diagnostico":   r[5],
            "tratamiento":   r[6],
            "paciente": {
                "id_paciente":    r[10],
                "nombre_completo": f"{r[7]} {r[8]} {r[9] or ''}".strip()
            },
            "doctor": {
                "nombre_completo": f"Dr. {r[11]} {r[12]} {r[13] or ''}".strip(),
                "especialidad":    r[14],
                "costo_consulta":  float(r[15]) if r[15] else 0.0,
            },
            "consultorio": {
                "numero": r[16],
                "piso":   r[17],
            },
            "pago": {
                "estatus": r[18],
                "monto":   float(r[19])
            }
        }), 200

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