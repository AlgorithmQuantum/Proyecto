from datetime import datetime

BITACORA = []

def registrar_evento(usuario, accion, detalle=""):
    evento = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "usuario": usuario,
        "accion": accion,
        "detalle": detalle
    }
    BITACORA.append(evento)