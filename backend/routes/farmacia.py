from flask import Blueprint, render_template, redirect, jsonify, request
from utils.decorador import login_requerido, rol_requerido
from database.db import get_coneccion
import pyodbc
import json

farmacia_bp = Blueprint("farmacia", __name__, url_prefix="/farmacia")

# ==========================================
# RUTAS DE VISTAS (HTML)
# ==========================================

@farmacia_bp.route("/dashboard") # Asumiendo que esta es inicioFarmacia.html
@login_requerido
@rol_requerido("Farmaceutico")
def farmacia_dashboard():
    return render_template("farmacia/inicioFarmacia.html")

@farmacia_bp.route("/validacion")
@login_requerido
@rol_requerido("Farmaceutico")
def farmaciaValidacion():
    return render_template("farmacia/validacionReceta.html")

@farmacia_bp.route("/historialVentas")
@login_requerido
@rol_requerido("Farmaceutico")
def farmaciaHistorialVentas():
    return render_template("farmacia/historial.html")

@farmacia_bp.route("/ventas")
@login_requerido
@rol_requerido("Farmaceutico")
def farmaciaVender():
    return render_template("farmacia/venta.html")

@farmacia_bp.route("/proveedores")
@login_requerido
@rol_requerido("Farmaceutico")
def proveedores():
    return render_template("farmacia/proveedores.html")

@farmacia_bp.route("/exito")
@login_requerido
@rol_requerido("Farmaceutico")
def pedidoExitoso():
    return render_template("farmacia/pedidoExito.html")

# ==========================================
# ENDPOINTS API (DATOS DINÁMICOS)
# ==========================================

@farmacia_bp.route("/api/inventario", methods=["GET"])
@login_requerido
@rol_requerido("Farmaceutico")
def obtener_inventario():
    try:
        with get_coneccion() as conn:
            cursor = conn.cursor()
            # Simulación de Categoría y Requiere_Receta usando CASE WHEN
            cursor.execute("""
                SELECT 
                    Id_medicamento, 
                    Nombre, 
                    ISNULL(Descripcion, 'Sin descripción') AS Descripcion, 
                    ISNULL(Concentracion, '') AS Concentracion, 
                    Precio, 
                    Stock,
                    CASE 
                        WHEN Nombre LIKE '%Amoxicilina%' OR Nombre LIKE '%Ciprofloxacino%' THEN 'Antibiótico'
                        WHEN Nombre LIKE '%Tramadol%' OR Nombre LIKE '%Clonazepam%' OR Nombre LIKE '%Diazepam%' 
                          OR Nombre LIKE '%Insulina%' OR Nombre LIKE '%Metformina%' THEN 'Controlado'
                        WHEN Nombre LIKE '%Jeringa%' OR Nombre LIKE '%Gasas%' OR Nombre LIKE '%Algodón%' THEN 'Insumo Médico'
                        ELSE 'Medicamento Libre'
                    END AS Categoria,
                    CASE 
                        WHEN Nombre LIKE '%Amoxicilina%' OR Nombre LIKE '%Ciprofloxacino%'
                          OR Nombre LIKE '%Tramadol%' OR Nombre LIKE '%Clonazepam%' OR Nombre LIKE '%Diazepam%'
                          OR Nombre LIKE '%Insulina%' OR Nombre LIKE '%Metformina%' OR Nombre LIKE '%Gabapentina%' THEN 1
                        ELSE 0
                    END AS Requiere_Receta
                FROM MEDICAMENTO
                ORDER BY Nombre
            """)
            columnas = [column[0] for column in cursor.description]
            inventario = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        return jsonify(inventario), 200
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500

@farmacia_bp.route("/procesar_pedido", methods=["POST"])
@login_requerido
@rol_requerido("Farmaceutico")
def procesar_pedido():
    try:
        # Se recibe el string JSON enviado desde el input oculto en proveedores.html
        datos_json = request.form.get('datos_pedido_json')
        if datos_json:
            pedido_lista = json.loads(datos_json)
            # AQUÍ A FUTURO: Insertar en una tabla PEDIDO_PROVEEDOR
            # Por ahora simulamos éxito redirigiendo a la vista
        return redirect("/farmacia/exito")
    except Exception as e:
        return redirect("/farmacia/proveedores")

@farmacia_bp.route("/api/historial-simulado", methods=["GET"])
@login_requerido
@rol_requerido("Farmaceutico")
def obtener_historial():
    # Retornamos un JSON vacío o simulado ya que no existe tabla BITACORA_FARMACIA
    return jsonify([]), 200