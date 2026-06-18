from flask import Blueprint, render_template, session, request
from utils.decorador import login_requerido, rol_requerido
from database.db import get_coneccion
from datetime import datetime, timedelta

recepcion_bp = Blueprint("recepcion", __name__, url_prefix="/recepcion")

def td_to_time(val):
    if isinstance(val, timedelta):
        total = int(val.total_seconds())
        from datetime import time as dt_time
        return dt_time(total // 3600, (total % 3600) // 60)
    return val

@recepcion_bp.route("/agenda")
@login_requerido
@rol_requerido(["Recepcionista"])
def agenda():
    fecha_param = request.args.get("fecha", datetime.now().strftime("%Y-%m-%d"))
    
    with get_coneccion() as conn:
        cursor = conn.cursor()
        # Traemos todas las citas de esa fecha usando la vista mejorada
        cursor.execute("""
            SELECT 
                Id_cita, Paciente, Fecha_cita, hora_cita, Hora_Fin, 
                Estatus, Doctor, Especialidad, Consultorio,
                -- Subconsulta para saber si ya se atendió
                (SELECT TOP 1 Id_receta FROM CITA c2 WHERE c2.Id_cita = V.Id_cita) AS Id_receta
            FROM VW_Detalle_Cita_Paciente V
            WHERE Fecha_cita = ?
            ORDER BY hora_cita ASC
        """, fecha_param)
        filas = cursor.fetchall()

    citas_dia = []
    for r in filas:
        estatus_texto = "Programada"
        if r[5] == 0:
            estatus_texto = "Cancelada"
        elif r[9] is not None:
            estatus_texto = "En Consulta" # o Atendida
        elif r[5] == 1:
            estatus_texto = "Programada" # Aquí puedes añadir lógica de "En Espera" después (ej. si hizo checkin)

        citas_dia.append({
            "id_cita": r[0],
            "paciente": r[1],
            "hora_inicio": str(td_to_time(r[3]))[:5],
            "hora_fin": str(td_to_time(r[4]))[:5] if r[4] else "00:00",
            "doctor": r[6],
            "especialidad": r[7],
            "estatus": estatus_texto
        })

    return render_template("recepcion/agendaCita.html", citas=citas_dia, fecha_actual=fecha_param, nombre_completo=session.get("nombre_completo"))

@recepcion_bp.route("/doctores")
@login_requerido
@rol_requerido(["Recepcionista"])
def doctores():
    # Esta misma lógica sirve para 'consultorios.html'
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                esp.Nombre AS Especialidad,
                e.Nombre + ' ' + e.Apellido_Paterno AS Doctor,
                h.Dia, h.Hora_Inicio, h.Hora_Fin,
                con.Numero AS Consultorio, con.Piso
            FROM DOCTOR d
            JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
            JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
            LEFT JOIN EMPLEADO_HORARIO eh ON e.Id_empleado = eh.Id_empleado
            LEFT JOIN HORARIO h ON eh.Id_Horario = h.Id_Horario
            LEFT JOIN CONSULTORIO con ON d.Id_doctor = con.Id_Doctor
            ORDER BY esp.Nombre, e.Apellido_Paterno
        """)
        filas = cursor.fetchall()

    # Agrupar doctores por especialidad
    especialidades_dict = {}
    for r in filas:
        esp = r[0]
        if esp not in especialidades_dict:
            especialidades_dict[esp] = []
        
        especialidades_dict[esp].append({
            "nombre": f"Dr. {r[1]}",
            "dia": r[2],
            "hora_inicio": str(td_to_time(r[3]))[:5] if r[3] else "",
            "consultorio": r[5] or "S/N",
            "piso": r[6] or "PB"
        })

    return render_template("recepcion/doctores.html", especialidades=especialidades_dict, nombre_completo=session.get("nombre_completo"))

@recepcion_bp.route("/caja")
@login_requerido
@rol_requerido("Recepcionista")
def caja():
    return render_template("recepcionista/caja.html", nombre_completo=session.get("nombre_completo"))

@recepcion_bp.route("/horarios")
@login_requerido
@rol_requerido("Recepcionista")
def horarios():
    return render_template("recepcionista/horarios.html", nombre_completo=session.get("nombre_completo"))

@recepcion_bp.route("/pacientes")
@login_requerido
@rol_requerido(["Recepcionista"])
def pacientes():
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                Id_paciente, Nombre, Apellido_Paterno, Telefono, Correo,
                ISNULL(Edad, DATEDIFF(YEAR, Fecha_nacimiento, GETDATE())) AS Edad,
                (SELECT TOP 1 Fecha_cita FROM CITA c WHERE c.Id_paciente = p.Id_paciente ORDER BY Fecha_cita DESC) AS Ultima_Visita
            FROM PACIENTE p
            ORDER BY Apellido_Paterno
        """)
        filas = cursor.fetchall()
        
        lista_pacientes = []
        for r in filas:
            lista_pacientes.append({
                "id": r[0], "nombre": r[1], "apellido": r[2], 
                "telefono": r[3], "correo": r[4], "edad": r[5], "ultima_visita": r[6]
            })

    return render_template("recepcion/pacientes.html", pacientes=lista_pacientes, nombre_completo=session.get("nombre_completo"))

@recepcion_bp.route("/paciente/<int:id_paciente>")
@login_requerido
@rol_requerido(["Recepcionista"])
def perfil_paciente(id_paciente):
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Id_paciente, Nombre, Apellido_Paterno, Apellido_Materno, Telefono, Correo,
                   Fecha_nacimiento, Tipo_sangre, ISNULL(Edad, DATEDIFF(YEAR, Fecha_nacimiento, GETDATE())) AS Edad
            FROM PACIENTE WHERE Id_paciente = ?
        """, id_paciente)
        paciente = cursor.fetchone()
        
        cursor.execute("""
            SELECT c.Fecha_cita, c.hora_cita, d.Id_doctor, e.Nombre + ' ' + e.Apellido_Paterno AS Doctor, 
                   esp.Nombre AS Especialidad, c.Estatus, t.Estatus_pago
            FROM CITA c
            JOIN DOCTOR d ON c.Id_doctor = d.Id_doctor
            JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
            JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
            LEFT JOIN TICKET t ON c.Id_cita = t.Id_cita
            WHERE c.Id_paciente = ?
            ORDER BY c.Fecha_cita DESC
        """, id_paciente)
        historial = cursor.fetchall()
        
    return render_template("recepcion/perfilPaciente.html", paciente=paciente, historial=historial, nombre_completo=session.get("nombre_completo"))

@recepcion_bp.route("/consultorios")
@login_requerido
@rol_requerido("Recepcionista")
def consultorios():
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                esp.Nombre AS Especialidad,
                e.Nombre + ' ' + e.Apellido_Paterno AS Doctor,
                h.Dia, h.Hora_Inicio, h.Hora_Fin,
                con.Numero AS Consultorio, con.Piso
            FROM DOCTOR d
            JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
            JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
            LEFT JOIN EMPLEADO_HORARIO eh ON e.Id_empleado = eh.Id_empleado
            LEFT JOIN HORARIO h ON eh.Id_Horario = h.Id_Horario
            LEFT JOIN CONSULTORIO con ON d.Id_doctor = con.Id_Doctor
            ORDER BY esp.Nombre, e.Apellido_Paterno
        """)
        filas = cursor.fetchall()

    # Agrupar doctores por especialidad
    especialidades_dict = {}
    for r in filas:
        esp = r[0]
        if esp not in especialidades_dict:
            especialidades_dict[esp] = []
        
        especialidades_dict[esp].append({
            "nombre": f"Dr. {r[1]}",
            "dia": r[2],
            "hora_inicio": str(td_to_time(r[3]))[:5] if r[3] else "",
            "consultorio": r[5] or "S/N",
            "piso": r[6] or "PB"
        })
    return doctores()

@recepcion_bp.route("/agendar-cita")
@login_requerido
@rol_requerido("Recepcionista")
def agendar_cita():
    return render_template("recepcionista/agendarCita.html")

@recepcion_bp.route("/doctor/<int:id_doctor>")
@login_requerido
@rol_requerido(["Recepcionista"])
def perfil_doctor(id_doctor):
    with get_coneccion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.Id_doctor, e.Nombre, e.Apellido_Paterno, e.Telefono, e.Correo,
                   esp.Nombre AS Especialidad, con.Numero AS Consultorio, con.Piso
            FROM DOCTOR d
            JOIN EMPLEADO e ON d.Id_empleado = e.Id_empleado
            JOIN ESPECIALIDAD esp ON d.Id_especialidad = esp.Id_especialidad
            LEFT JOIN CONSULTORIO con ON d.Id_doctor = con.Id_Doctor
            WHERE d.Id_doctor = ?
        """, id_doctor)
        doctor = cursor.fetchone()
        
        cursor.execute("""
            SELECT h.Dia, h.Hora_Inicio, h.Hora_Fin
            FROM EMPLEADO_HORARIO eh
            JOIN DOCTOR d ON eh.Id_empleado = d.Id_empleado
            JOIN HORARIO h ON eh.Id_Horario = h.Id_Horario
            WHERE d.Id_doctor = ?
        """, id_doctor)
        horarios = cursor.fetchall()
        
    return render_template("recepcion/perfilDoctor.html", doctor=doctor, horarios=horarios, nombre_completo=session.get("nombre_completo"))

@recepcion_bp.route("/nuevo-paciente")
@login_requerido
@rol_requerido(["Recepcionista"])
def nuevo_paciente():
    return render_template("recepcion/nuevoPaciente.html", nombre_completo=session.get("nombre_completo"))

@recepcion_bp.route("/nuevo-doctor")
@login_requerido
@rol_requerido(["Recepcionista", "Administrador"])
def nuevo_doctor():
    return render_template("recepcion/nuevoDoctor.html", nombre_completo=session.get("nombre_completo"))

@recepcion_bp.route("/nueva-recepcion")
@login_requerido
@rol_requerido(["Administrador"])
def nueva_recepcion():
    return render_template("recepcion/nuevaRecepcion.html", nombre_completo=session.get("nombre_completo"))