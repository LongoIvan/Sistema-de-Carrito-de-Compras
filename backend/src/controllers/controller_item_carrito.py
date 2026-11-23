from backend.src.models.model_item_carrito import ItemCarrito
from flask import Blueprint, jsonify, request
from backend.src.database.database import fetch_all, execute_query, execute_query_returning

items_carrito_bp = Blueprint("items_carrito", __name__)

@items_carrito_bp.route("/api/carritos/<int:idcarrito>/items", methods=["POST"])
def agregar_item(idcarrito):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({"error": "Datos invalidos"}), 400

    idproducto = datos.get("idproducto")
    cantidad = datos.get("cantidad")

    if type(idproducto) is not int or idproducto <= 0:
        return jsonify({"error": "ID de producto invalido"}), 400

    if type(cantidad) is not int or cantidad <= 0:
        return jsonify({"error": "Cantidad invalida"}), 400

    carritos = fetch_all("SELECT * FROM carrito")

    carrito = next(
        (c for c in carritos if c["idcarrito"] == idcarrito),
        None
    )

    if carrito is None:
        return jsonify({"error": "Carrito no encontrado"}), 404

    if carrito["estado"] != "Pendiente":
        return jsonify({"error": "El carrito no esta pendiente"}), 400

    productos = fetch_all("SELECT * FROM producto")

    producto = next(
        (p for p in productos if p["idproducto"] == idproducto),
        None
    )

    if producto is None:
        return jsonify({"error": "Producto no encontrado"}), 404

    if producto["stock"] < cantidad:
        return jsonify({"error": "Stock insuficiente"}), 400

    consulta = """
        INSERT INTO item_carrito
            (idcarrito, id_item_producto, cantidad, precio_unitario)
        VALUES (%s, %s, %s, %s)
        RETURNING id_item_carrito
    """

    resultado = execute_query_returning(
        consulta,
        (idcarrito, idproducto, cantidad, producto["precio"])
    )

    return jsonify({
        "mensaje": "Producto agregado al carrito correctamente",
        "id_item_carrito": resultado["id_item_carrito"],
        "idcarrito": idcarrito,
        "idproducto": idproducto,
        "cantidad": cantidad,
        "precio_unitario": float(producto["precio"])
    }), 201

@items_carrito_bp.route("/api/carritos/<int:idcarrito>/items/<int:iditem>/aumentar", methods=["PATCH"])
def aumentar_cantidad(idcarrito, iditem):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({"error": "Datos invalidos"}), 400

    cantidad = datos.get("cantidad")

    if type(cantidad) is not int or cantidad <= 0:
        return jsonify({"error": "Cantidad invalida"}), 400

    carritos = fetch_all("SELECT * FROM carrito")

    carrito = next(
        (c for c in carritos if c["idcarrito"] == idcarrito),
        None
    )

    if carrito is None:
        return jsonify({"error": "Carrito no encontrado"}), 404

    if carrito["estado"] != "Pendiente":
        return jsonify({"error": "El carrito no esta pendiente"}), 400

    items = fetch_all("SELECT * FROM item_carrito")

    item = next(
        (i for i in items
         if i["id_item_carrito"] == iditem
         and i["idcarrito"] == idcarrito),
        None
    )

    if item is None:
        return jsonify({"error": "Item no encontrado en este carrito"}), 404

    productos = fetch_all("SELECT * FROM producto")

    producto = next(
        (p for p in productos
         if p["idproducto"] == item["id_item_producto"]),
        None
    )

    if producto is None:
        return jsonify({"error": "Producto no encontrado"}), 404

    nueva_cantidad = item["cantidad"] + cantidad

    if nueva_cantidad > producto["stock"]:
        return jsonify({"error": "Stock insuficiente"}), 400

    consulta = """
        UPDATE item_carrito
        SET cantidad = %s
        WHERE id_item_carrito = %s
          AND idcarrito = %s
    """

    execute_query(consulta, (nueva_cantidad, iditem, idcarrito))

    return jsonify({
        "mensaje": "Cantidad aumentada correctamente",
        "idcarrito": idcarrito,
        "id_item_carrito": iditem,
        "cantidad_anterior": item["cantidad"],
        "cantidad_agregada": cantidad,
        "cantidad_actual": nueva_cantidad
    }), 200

@items_carrito_bp.route("/api/carritos/<int:idcarrito>/items/<int:iditem>/disminuir", methods=["PATCH"])
def disminuir_cantidad(idcarrito, iditem):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({"error": "Datos invalidos"}), 400

    cantidad = datos.get("cantidad")

    if type(cantidad) is not int or cantidad <= 0:
        return jsonify({"error": "Cantidad invalida"}), 400

    carritos = fetch_all("SELECT * FROM carrito")

    carrito = next(
        (c for c in carritos if c["idcarrito"] == idcarrito),
        None
    )

    if carrito is None:
        return jsonify({"error": "Carrito no encontrado"}), 404

    if carrito["estado"] != "Pendiente":
        return jsonify({"error": "El carrito no esta pendiente"}), 400

    items = fetch_all("SELECT * FROM item_carrito")

    item = next(
        (i for i in items
         if i["id_item_carrito"] == iditem
         and i["idcarrito"] == idcarrito),
        None
    )

    if item is None:
        return jsonify({"error": "Item no encontrado en este carrito"}), 404

    nueva_cantidad = item["cantidad"] - cantidad

    if nueva_cantidad < 0:
        return jsonify({
            "error": "No podes disminuir mas unidades de las existentes"
        }), 400

    if nueva_cantidad == 0:
        consulta = """
            DELETE FROM item_carrito
            WHERE id_item_carrito = %s
              AND idcarrito = %s
        """

        execute_query(consulta, (iditem, idcarrito))

        return jsonify({
            "mensaje": "Item eliminado del carrito",
            "idcarrito": idcarrito,
            "id_item_carrito": iditem,
            "cantidad_eliminada": cantidad
        }), 200

    consulta = """
        UPDATE item_carrito
        SET cantidad = %s
        WHERE id_item_carrito = %s
          AND idcarrito = %s
    """

    execute_query(consulta, (nueva_cantidad, iditem, idcarrito))

    return jsonify({
        "mensaje": "Cantidad disminuida correctamente",
        "idcarrito": idcarrito,
        "id_item_carrito": iditem,
        "cantidad_anterior": item["cantidad"],
        "cantidad_disminuida": cantidad,
        "cantidad_actual": nueva_cantidad
    }), 200

# #Devolver datos

# def mostrar_id(item_carrito:ItemCarrito):
#     return item_carrito.id_item_carrito

# def mostrar_id_producto(item_carrito:ItemCarrito):
#     return item_carrito.id_item_producto

# def mostrar_cantidad(item_carrito:ItemCarrito):
#     return item_carrito.cantidad

# def mostar_precio(item_carrito:ItemCarrito):
#     return item_carrito.precio_unitario

# #Metodos

# def modificar_cantidad(item_carrito:ItemCarrito):
#     def aumentar(num:int):
#         if num.isdigit():
#             item_carrito.cantidad += num
#         else:
#             print("--ERROR - Valor Invalido--")
#             return

#     def disminuir(num:int):
#         if num.isdigit():
#             if num > item_carrito.cantidad:
#                 item_carrito.cantidad = 1
#             else:
#                 item_carrito.cantidad -= num
#         else:
#             print("--ERROR - Valor Invalido--")
#             return

# def calcular_subtotal(item_carrito:ItemCarrito):
#     sub_total = 0
#     sub_total = item_carrito.cantidad * item_carrito.precio_unitario
#     return sub_total