from flask import Flask
from routes.auth import auth_bp
from routes.citas import citas_bp
from datetime import timedelta
from utils.decorador import login_requerido, rol_requerido

def create_app():
    app = Flask(__name__)
    app.secret_key = "Hospital_ESCOM_BD_Proyecto_2026"
    app.permanent_session_lifetime = timedelta(minutes=30)

    app.register_blueprint(auth_bp)
    app.register_blueprint(citas_bp)

    @app.route("/")
    def index():
        return {"mensaje": "API Hospital (BD falsa)"}

    #ruta provisional en revision
    @app.route("/dashboard/paciente")
    @login_requerido
    @rol_requerido("Paciente")
    def dashboard_paciente():
        return "Panel Paciente"

    #ruta provisional en revision
    @app.route("/dashboard/admin")
    @login_requerido
    @rol_requerido("Recepcionista")
    def dashboard_admin():
        return "Panel Administrativo"
    
    #ruta de prueba
    app.route("/bitacora")
    def ver_bitacora():
        from utils.bitacora import BITACORA
        return {"bitacora": BITACORA}
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)