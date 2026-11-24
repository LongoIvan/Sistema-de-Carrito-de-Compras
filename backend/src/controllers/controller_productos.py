from flask import Blueprint, jsonify, request
import math
from backend.src.database.database import fetch_all, execute_query
from backend.src.models.model_productos import Categoria
from psycopg2.errors import ForeignKeyViolation, RestrictViolation

productos_bp = Blueprint("productos", __name__)


@productos_bp.route("/api/productos", methods=["GET"])
def listar_productos():
    consulta = """
        SELECT idproducto, nombre, precio, stock,
               categoria, fecha, activo, descripcion
        FROM producto
    """

    productos = fetch_all(consulta)

    for producto in productos:
        if producto["fecha"] is not None:
            producto["fecha"] = producto["fecha"].isoformat()

        producto["precio"] = float(producto["precio"])

    return jsonify(productos), 200



@productos_bp.route("/api/productos/<int:id>/nombre", methods=["GET"])
def mostrar_nombre(id):
    consulta = "SELECT idproducto, nombre FROM producto"
    productos = fetch_all(consulta)

    for producto in productos:
        if producto["idproducto"] == id:
            return jsonify({"nombre": producto["nombre"]}), 200

    return jsonify({"error": "Producto no encontrado"}), 404

@productos_bp.route("/api/productos/<int:id>/precio", methods=["GET"])
def mostrar_precio(id):
    consulta = "SELECT idproducto, precio FROM producto"
    productos = fetch_all(consulta)

    for producto in productos:
        if producto["idproducto"] == id:
            return jsonify({"precio": float(producto["precio"])}), 200

    return jsonify({"error": "Producto no encontrado"}), 404

@productos_bp.route("/api/productos/<int:id>/stock", methods=["GET"])
def mostrar_stock(id):
    consulta = "SELECT idproducto, stock FROM producto"
    productos = fetch_all(consulta)

    for producto in productos:
        if producto["idproducto"] == id:
            return jsonify({"stock": producto["stock"]}), 200

    return jsonify({"error": "Producto no encontrado"}), 404

@productos_bp.route("/api/productos/<int:id>/categoria", methods=["GET"])
def mostrar_categoria (id):
    consulta = "SELECT idproducto, categoria FROM producto"
    productos = fetch_all(consulta)

    for producto in productos:
        if producto["idproducto"] == id:
            return jsonify({"categoria": producto["categoria"]}), 200

    return jsonify({"error": "Producto no encontrado"}), 404

@productos_bp.route("/api/productos/<int:id>/fecha", methods=["GET"])
def mostrar_fecha(id):
    consulta = "SELECT idproducto, fecha FROM producto"
    productos = fetch_all(consulta)

    for producto in productos:
        if producto["idproducto"] == id:
            if producto["fecha"] is not None:
                return jsonify({"fecha": producto["fecha"].isoformat()}), 200

            return jsonify({"fecha": None}), 200

    return jsonify({"error": "Producto no encontrado"}), 404

@productos_bp.route("/api/productos/<int:id>/descripcion", methods=["GET"])
def mostrar_descripcion (id):
    consulta = "SELECT idproducto, descripcion FROM producto"
    productos = fetch_all(consulta)

    for producto in productos:
        if producto["idproducto"] == id:
            return jsonify({"descripcion": producto["descripcion"]}), 200

    return jsonify({"error": "Producto no encontrado"}), 404


@productos_bp.route("/api/productos", methods=["POST"])
def agregar_productos():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({"error": "JSON invalido"}), 400

    campos = ["nombre", "precio", "stock", "categoria", "descripcion"]

    for campo in campos:
        if campo not in datos:
            return jsonify({"error": f"Falta el campo {campo}"}), 400

    nombre = datos["nombre"]
    precio = datos["precio"]
    stock = datos["stock"]
    categoria = datos["categoria"]
    descripcion = datos["descripcion"]

    # Validar nombre
    if not isinstance(nombre, str) or not nombre.strip():
        return jsonify({"error": "Nombre invalido"}), 400

    nombre = nombre.strip()

    # Validar precio
    if type(precio) not in (int, float) or not math.isfinite(precio) or precio < 0:
        return jsonify({"error": "Precio invalido"}), 400

    # Validar stock
    if type(stock) is not int or stock < 0:
        return jsonify({"error": "Stock invalido"}), 400

    
    # Validar categoria
    if not isinstance(categoria, str) or not categoria.strip():
        return jsonify({"error": "Categoria invalida"}), 400

    categoria = categoria.strip()

    categoriasValidas = [categoria.value for categoria in Categoria]

    if categoria not in categoriasValidas:
        return jsonify({
            "error": "Categoria no valida",
            "categorias_permitidas": categoriasValidas
        }), 400

    # Validar descripcion
    if not isinstance(descripcion, str) or not descripcion.strip():
        return jsonify({"error": "Descripcion invalida"}), 400

    descripcion = descripcion.strip()

    # Determinar si el producto esta activo
    activo = stock > 0

    consulta = """
        INSERT INTO producto
        (nombre, precio, stock, categoria, fecha, activo, descripcion)
        VALUES (%s, %s, %s, %s, CURRENT_DATE, %s, %s)
    """

    execute_query(
        consulta,
        (nombre, precio, stock, categoria, activo, descripcion)
    )

    return jsonify({
        "mensaje": "Producto agregado correctamente",
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
        "categoria": categoria,
        "activo": activo
    }), 201

@productos_bp.route("/api/productos/<int:id>/precio", methods=["PATCH"])
def modificar_precio(id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "precio" not in datos:
        return jsonify({"error": "Datos incompletos"}), 400

    nuevoPrecio = datos["precio"]

    if type(nuevoPrecio) not in (int, float):
        return jsonify({"error": "El precio debe ser un numero"}), 400

    if not math.isfinite(nuevoPrecio) or nuevoPrecio < 0:
        return jsonify({"error": "El precio debe ser un numero finito y no negativo"}), 400

    consulta = "UPDATE producto SET precio = %s WHERE idproducto = %s"

    filas = execute_query(consulta, (nuevoPrecio, id))

    if filas == 0:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify({
        "mensaje": "Precio actualizado correctamente",
        "precio": nuevoPrecio
    }), 200

@productos_bp.route("/api/productos/<int:id>/stock", methods=["PATCH"])
def modificar_stock(id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "stock" not in datos:
        return jsonify({"error": "Datos incompletos"}), 400

    nuevoStock = datos["stock"]

    if type(nuevoStock) is not int:
        return jsonify({"error": "El stock debe ser un numero entero"}), 400

    if nuevoStock < 0:
        return jsonify({"error": "El stock no puede ser negativo"}), 400

    activo = nuevoStock > 0

    consulta = """
        UPDATE producto
        SET stock = %s, activo = %s
        WHERE idproducto = %s
    """

    filas = execute_query(consulta, (nuevoStock, activo, id))

    if filas == 0:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify({
        "mensaje": "Stock actualizado correctamente",
        "stock": nuevoStock,
        "activo": activo
    }), 200

@productos_bp.route("/api/productos/<int:id>/stock/agregar", methods=["PATCH"])
def agregar_stock(id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "stock" not in datos:
        return jsonify({"error": "Datos incompletos"}), 400

    stockAgregar = datos["stock"]

    if type(stockAgregar) is not int:
        return jsonify({"error": "El stock debe ser un numero entero"}), 400

    if stockAgregar <= 0:
        return jsonify({"error": "La cantidad a agregar debe ser mayor a 0"}), 400

    consulta = """
        UPDATE producto
        SET stock = stock + %s, activo = TRUE
        WHERE idproducto = %s
    """

    filas = execute_query(consulta, (stockAgregar, id))

    if filas == 0:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify({
        "mensaje": "Stock agregado correctamente",
        "cantidad_agregada": stockAgregar
    }), 200

@productos_bp.route("/api/productos/<int:id>/stock/quitar", methods=["PATCH"])
def quitar_stock(id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "stock" not in datos:
        return jsonify({"error": "Datos incompletos"}), 400

    stockQuitar = datos["stock"]

    if type(stockQuitar) is not int:
        return jsonify({"error": "El stock debe ser un numero entero"}), 400

    if stockQuitar <= 0:
        return jsonify({"error": "La cantidad a quitar debe ser mayor a 0"}), 400

    consulta = """
        UPDATE producto
        SET stock = stock - %s,
            activo = (stock - %s > 0)
        WHERE idproducto = %s AND stock >= %s
    """

    filas = execute_query(
        consulta,
        (stockQuitar, stockQuitar, id, stockQuitar)
    )

    if filas == 0:
        productos = fetch_all("SELECT idproducto FROM producto")

        for producto in productos:
            if producto["idproducto"] == id:
                return jsonify({"error": "Stock insuficiente"}), 400

        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify({
        "mensaje": "Stock descontado correctamente",
        "cantidad_descontada": stockQuitar
    }), 200

@productos_bp.route("/api/productos/<int:id>/nombre", methods=["PATCH"])
def modificar_nombre(id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "nombre" not in datos:
        return jsonify({"error": "Datos incompletos"}), 400

    nuevoNombre = datos["nombre"]

    if type(nuevoNombre) is not str:
        return jsonify({"error": "El nombre debe ser un texto"}), 400

    nuevoNombre = nuevoNombre.strip()

    if not nuevoNombre:
        return jsonify({"error": "El nombre no puede estar vacio"}), 400

    consulta = "UPDATE producto SET nombre = %s WHERE idproducto = %s"

    filas = execute_query(consulta, (nuevoNombre, id))

    if filas == 0:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify({
        "mensaje": "Nombre actualizado correctamente",
        "nombre": nuevoNombre
    }), 200

@productos_bp.route("/api/productos/<int:id>/descripcion", methods=["PATCH"])
def modificar_descripcion(id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "descripcion" not in datos:
        return jsonify({"error": "Datos incompletos"}), 400

    nuevaDescripcion = datos["descripcion"]

    if type(nuevaDescripcion) is not str:
        return jsonify({"error": "La descripcion debe ser un texto"}), 400

    nuevaDescripcion = nuevaDescripcion.strip()

    if not nuevaDescripcion:
        return jsonify({"error": "La descripcion no puede estar vacia"}), 400

    consulta = "UPDATE producto SET descripcion = %s WHERE idproducto = %s"

    filas = execute_query(consulta, (nuevaDescripcion, id))

    if filas == 0:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify({
        "mensaje": "Descripcion actualizada correctamente",
        "descripcion": nuevaDescripcion
    }), 200

@productos_bp.route("/api/productos/<int:id>/categoria", methods=["PATCH"])
def modificar_categoria(id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "categoria" not in datos:
        return jsonify({"error": "Datos incompletos"}), 400

    nuevaCategoria = datos["categoria"]

    if type(nuevaCategoria) is not str:
        return jsonify({"error": "La categoria debe ser un texto"}), 400

    nuevaCategoria = nuevaCategoria.strip()

    if not nuevaCategoria:
        return jsonify({"error": "La categoria no puede estar vacia"}), 400

    categoriasValidas = [categoria.value for categoria in Categoria]

    if nuevaCategoria not in categoriasValidas:
        return jsonify({
            "error": "Categoria no valida",
            "categorias_permitidas": categoriasValidas
        }), 400

    consulta = "UPDATE producto SET categoria = %s WHERE idproducto = %s"

    filas = execute_query(consulta, (nuevaCategoria, id))

    if filas == 0:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify({
        "mensaje": "Categoria actualizada correctamente",
        "categoria": nuevaCategoria
    }), 200

@productos_bp.route("/api/productos/<int:id>", methods=["DELETE"])
def eliminar_producto(id):

    consulta = "DELETE FROM producto WHERE idproducto = %s"

    try:
        filas = execute_query(consulta, (id,))
    except (ForeignKeyViolation, RestrictViolation):
        return jsonify({
            "error": "No se puede eliminar un producto asociado a carritos"
        }), 409

    if filas == 0:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify({
        "mensaje": "Producto eliminado correctamente",
        "idproducto": id
    }), 200