from functools import wraps
from flask import session, jsonify, redirect

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "id_usuario" not in session:
            return jsonify({"error": "No has iniciado sesión"}), 401
        return func(*args, **kwargs)
    return wrapper


def role_required(roles_permitidos):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "rol" not in session:
                return jsonify({"error": "No autorizado"}), 401

            if session["rol"] not in roles_permitidos:
                return jsonify({"error": "Acceso denegado"}), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator
