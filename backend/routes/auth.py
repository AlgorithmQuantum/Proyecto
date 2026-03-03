from flask import Blueprint, request, render_template, redirect, session
from db_fake import USUARIOS  # o db real luego
from werkzeug.security import generate_password_hash, check_password_hash
from utils.bitacora import registrar_evento

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


#ruta para logearse
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    usuario = request.form.get("usuario")
    password = request.form.get("password")
    recordar = request.form.get("recordar")

    for u in USUARIOS:
        if u.get("usuario") == usuario and check_password_hash(u["password"], password):

            if recordar:
                session.permanent = True  # dura 30 minutos
            else:
                session.permanent = False  # se borra al cerrar navegador
            
            session["usuario_id"] = u["id"]
            session["nombre"] = u["nombre"]
            session["rol"] = u["rol"]

            return redirect("/dashboard")

    return render_template(
        "login.html",
        error="Usuario o contraseña incorrectos"
    )

#ruta para salir de sesion 
@auth_bp.route("/logout")
def logout():
    session.clear()
    registrar_evento(
        session.get("nombre", "Desconocido"),
        "LOGOUT",
        "Cierre de sesión"
    )
    return redirect("/auth/login")

#ruta para registrarse
@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    nombre = request.form.get("nombre")
    usuario = request.form.get("usuario")
    password = request.form.get("password")
    rol = request.form.get("rol")

    for u in USUARIOS:
        if u.get("usuario") == usuario:
            return render_template(
                "register.html",
                error="El usuario ya existe"
            )

    password_hash = generate_password_hash(password)

    nuevo_usuario = {
        "id": len(USUARIOS) + 1,
        "nombre": nombre,
        "usuario": usuario,
        "password": password_hash,  # HASH
        "rol": rol
    }

    USUARIOS.append(nuevo_usuario)

    registrar_evento(
        usuario,
        "LOGIN",
        "Inicio de sesión exitoso"
    )

    return redirect("/auth/login")