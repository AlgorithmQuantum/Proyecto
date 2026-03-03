from functools import wraps
from flask import session, redirect
from utils.bitacora import registrar_evento

def login_requerido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect("/auth/login")
        return func(*args, **kwargs)
    return wrapper


def rol_requerido(rol_necesario):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if "rol" not in session:
                return redirect("/auth/login")

            if session["rol"] != rol_necesario:
                registrar_evento(
                    session.get("nombre", "Desconocido"),
                    "ACCESO_DENEGADO",
                    f"Intentó entrar a {rol_necesario}"
                )
                return "No tienes permisos", 403

            return func(*args, **kwargs)

        return wrapper
    return decorator
