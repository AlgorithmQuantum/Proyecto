from flask import Blueprint, render_template
from utils.decorador import login_requerido, rol_requerido

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_requerido
@rol_requerido("Admin")
def admin_dashboard():
    return render_template("administracion/inicioAdmin.html")
