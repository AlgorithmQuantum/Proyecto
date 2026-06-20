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