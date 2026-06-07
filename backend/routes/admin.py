from flask import Blueprint, render_template
from utils.decorador import login_requerido, rol_requerido

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