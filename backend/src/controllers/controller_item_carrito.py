# Librerías de Python
from contextlib import closing

# Flask
from flask import Blueprint, jsonify, request, current_app

# Modelos
from backend.src.models.model_item_carrito import ItemCarrito

# Base de datos
from backend.src.database.database import (
    fetch_all,
    execute_query,
    execute_query_returning,
    get_connection
)
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

    with closing(get_connection(current_app.config["DATABASE_URL"])) as connection:
        with connection:
            with connection.cursor() as cursor:

                # 1. Bloquear y comprobar el carrito
                cursor.execute(
                    """
                    SELECT estado
                    FROM carrito
                    WHERE idcarrito = %s
                    FOR UPDATE
                    """,
                    (idcarrito,)
                )

                carrito = cursor.fetchone()

                if carrito is None:
                    return jsonify({"error": "Carrito no encontrado"}), 404

                if carrito["estado"] != "Pendiente":
                    return jsonify({
                        "error": "El carrito no esta pendiente"
                    }), 400

                # 2. Consultar el producto
                cursor.execute(
                    """
                    SELECT idproducto, nombre, precio, stock
                    FROM producto
                    WHERE idproducto = %s
                    """,
                    (idproducto,)
                )

                producto = cursor.fetchone()

                if producto is None:
                    return jsonify({"error": "Producto no encontrado"}), 404

                # 3. Buscar las unidades existentes en el carrito
                cursor.execute(
                    """
                    SELECT id_item_carrito, cantidad
                    FROM item_carrito
                    WHERE idcarrito = %s
                      AND id_item_producto = %s
                    ORDER BY id_item_carrito
                    """,
                    (idcarrito, idproducto)
                )

                items_existentes = cursor.fetchall()

                cantidad_en_carrito = sum(
                    item["cantidad"] for item in items_existentes
                )

                cantidad_total = cantidad_en_carrito + cantidad

                # 4. Validar el stock total solicitado
                if cantidad_total > producto["stock"]:
                    return jsonify({
                        "error": "Stock insuficiente",
                        "producto": producto["nombre"],
                        "stock_disponible": producto["stock"],
                        "cantidad_en_carrito": cantidad_en_carrito,
                        "cantidad_solicitada": cantidad,
                        "cantidad_total": cantidad_total
                    }), 400

                # 5. Si ya existe, actualizar el primer item
                if items_existentes:
                    iditem = items_existentes[0]["id_item_carrito"]

                    cursor.execute(
                        """
                        UPDATE item_carrito
                        SET cantidad = %s
                        WHERE id_item_carrito = %s
                          AND idcarrito = %s
                        """,
                        (cantidad_total, iditem, idcarrito)
                    )

                    # Eliminar posibles registros duplicados anteriores
                    cursor.execute(
                        """
                        DELETE FROM item_carrito
                        WHERE idcarrito = %s
                          AND id_item_producto = %s
                          AND id_item_carrito <> %s
                        """,
                        (idcarrito, idproducto, iditem)
                    )

                    mensaje = "Cantidad del producto actualizada correctamente"
                    codigo_estado = 200

                # 6. Si no existe, crear un nuevo item
                else:
                    cursor.execute(
                        """
                        INSERT INTO item_carrito
                            (idcarrito, id_item_producto, cantidad, precio_unitario)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id_item_carrito
                        """,
                        (
                            idcarrito,
                            idproducto,
                            cantidad,
                            producto["precio"]
                        )
                    )

                    resultado = cursor.fetchone()
                    iditem = resultado["id_item_carrito"]

                    mensaje = "Producto agregado al carrito correctamente"
                    codigo_estado = 201

    return jsonify({
        "mensaje": mensaje,
        "id_item_carrito": iditem,
        "idcarrito": idcarrito,
        "idproducto": idproducto,
        "cantidad_agregada": cantidad,
        "cantidad_total": cantidad_total,
        "precio_unitario": float(producto["precio"])
    }), codigo_estado





@items_carrito_bp.route("/api/carritos/<int:idcarrito>/items/<int:iditem>/aumentar", methods=["PATCH"])
def aumentar_cantidad(idcarrito, iditem):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({"error": "Datos invalidos"}), 400

    cantidad = datos.get("cantidad")

    if type(cantidad) is not int or cantidad <= 0:
        return jsonify({"error": "Cantidad invalida"}), 400

    with closing(get_connection(current_app.config["DATABASE_URL"])) as connection:
        with connection:
            with connection.cursor() as cursor:

                # 1. Bloquear el carrito
                cursor.execute(
                    "SELECT estado FROM carrito WHERE idcarrito = %s FOR UPDATE",
                    (idcarrito,)
                )

                carrito = cursor.fetchone()

                if carrito is None:
                    return jsonify({"error": "Carrito no encontrado"}), 404

                if carrito["estado"] != "Pendiente":
                    return jsonify({
                        "error": "El carrito no esta pendiente"
                    }), 400

                # 2. Buscar el item que queremos modificar
                cursor.execute(
                    """
                    SELECT *
                    FROM item_carrito
                    WHERE id_item_carrito = %s
                      AND idcarrito = %s
                    """,
                    (iditem, idcarrito)
                )

                item = cursor.fetchone()

                if item is None:
                    return jsonify({
                        "error": "Item no encontrado en este carrito"
                    }), 404

                # 3. Consultar el stock del producto
                cursor.execute(
                    """
                    SELECT nombre, stock
                    FROM producto
                    WHERE idproducto = %s
                    """,
                    (item["id_item_producto"],)
                )

                producto = cursor.fetchone()

                if producto is None:
                    return jsonify({"error": "Producto no encontrado"}), 404

                # 4. Sumar todas las unidades de ese producto
                cursor.execute(
                    """
                    SELECT COALESCE(SUM(cantidad), 0) AS cantidad_en_carrito
                    FROM item_carrito
                    WHERE idcarrito = %s
                      AND id_item_producto = %s
                    """,
                    (idcarrito, item["id_item_producto"])
                )

                resultado = cursor.fetchone()
                cantidad_en_carrito = resultado["cantidad_en_carrito"]

                cantidad_total = cantidad_en_carrito + cantidad

                # 5. Comprobar el stock total solicitado
                if cantidad_total > producto["stock"]:
                    return jsonify({
                        "error": "Stock insuficiente",
                        "producto": producto["nombre"],
                        "stock_disponible": producto["stock"],
                        "cantidad_en_carrito": cantidad_en_carrito,
                        "cantidad_solicitada": cantidad,
                        "cantidad_total": cantidad_total
                    }), 400

                # 6. Actualizar la cantidad del item
                nueva_cantidad = item["cantidad"] + cantidad

                cursor.execute(
                    """
                    UPDATE item_carrito
                    SET cantidad = %s
                    WHERE id_item_carrito = %s
                      AND idcarrito = %s
                    """,
                    (nueva_cantidad, iditem, idcarrito)
                )

    return jsonify({
        "mensaje": "Cantidad aumentada correctamente",
        "idcarrito": idcarrito,
        "id_item_carrito": iditem,
        "cantidad_anterior": item["cantidad"],
        "cantidad_agregada": cantidad,
        "cantidad_actual": nueva_cantidad,
        "cantidad_total_producto": cantidad_total
    }), 200




@items_carrito_bp.route("/api/carritos/<int:idcarrito>/items/<int:iditem>/disminuir", methods=["PATCH"])
def disminuir_cantidad(idcarrito, iditem):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({"error": "Datos invalidos"}), 400

    cantidad = datos.get("cantidad")

    if type(cantidad) is not int or cantidad <= 0:
        return jsonify({"error": "Cantidad invalida"}), 400

    with closing(get_connection(current_app.config["DATABASE_URL"])) as connection:
        with connection:
            with connection.cursor() as cursor:

                # Bloqueamos el carrito durante la modificacion
                cursor.execute(
                    "SELECT estado FROM carrito WHERE idcarrito = %s FOR UPDATE",
                    (idcarrito,)
                )

                carrito = cursor.fetchone()

                if carrito is None:
                    return jsonify({"error": "Carrito no encontrado"}), 404

                if carrito["estado"] != "Pendiente":
                    return jsonify({"error": "El carrito no esta pendiente"}), 400

                # Consultamos el item dentro de la misma transaccion
                cursor.execute(
                    """
                    SELECT *
                    FROM item_carrito
                    WHERE id_item_carrito = %s
                      AND idcarrito = %s
                    """,
                    (iditem, idcarrito)
                )

                item = cursor.fetchone()

                if item is None:
                    return jsonify({
                        "error": "Item no encontrado en este carrito"
                    }), 404

                nueva_cantidad = item["cantidad"] - cantidad

                if nueva_cantidad < 0:
                    return jsonify({
                        "error": "No podes disminuir mas unidades de las existentes"
                    }), 400

                if nueva_cantidad == 0:
                    cursor.execute(
                        """
                        DELETE FROM item_carrito
                        WHERE id_item_carrito = %s
                          AND idcarrito = %s
                        """,
                        (iditem, idcarrito)
                    )

                    mensaje = "Item eliminado del carrito"

                else:
                    cursor.execute(
                        """
                        UPDATE item_carrito
                        SET cantidad = %s
                        WHERE id_item_carrito = %s
                          AND idcarrito = %s
                        """,
                        (nueva_cantidad, iditem, idcarrito)
                    )

                    mensaje = "Cantidad disminuida correctamente"

    if nueva_cantidad == 0:
        return jsonify({
            "mensaje": mensaje,
            "idcarrito": idcarrito,
            "id_item_carrito": iditem,
            "cantidad_eliminada": cantidad
        }), 200

    return jsonify({
        "mensaje": mensaje,
        "idcarrito": idcarrito,
        "id_item_carrito": iditem,
        "cantidad_anterior": item["cantidad"],
        "cantidad_disminuida": cantidad,
        "cantidad_actual": nueva_cantidad
    }), 200


@items_carrito_bp.route("/api/carritos/<int:idcarrito>/items/<int:iditem>", methods=["DELETE"])
def eliminar_item(idcarrito, iditem):

    with closing(get_connection(current_app.config["DATABASE_URL"])) as connection:
        with connection:
            with connection.cursor() as cursor:

                # 1. Bloquear el carrito
                cursor.execute(
                    """
                    SELECT estado
                    FROM carrito
                    WHERE idcarrito = %s
                    FOR UPDATE
                    """,
                    (idcarrito,)
                )

                carrito = cursor.fetchone()

                if carrito is None:
                    return jsonify({"error": "Carrito no encontrado"}), 404

                if carrito["estado"] != "Pendiente":
                    return jsonify({
                        "error": "El carrito no esta pendiente"
                    }), 400

                # 2. Comprobar que el item pertenece al carrito
                cursor.execute(
                    """
                    SELECT id_item_carrito, id_item_producto, cantidad
                    FROM item_carrito
                    WHERE id_item_carrito = %s
                      AND idcarrito = %s
                    """,
                    (iditem, idcarrito)
                )

                item = cursor.fetchone()

                if item is None:
                    return jsonify({
                        "error": "Item no encontrado en este carrito"
                    }), 404

                # 3. Eliminar el item completo
                cursor.execute(
                    """
                    DELETE FROM item_carrito
                    WHERE id_item_carrito = %s
                      AND idcarrito = %s
                    """,
                    (iditem, idcarrito)
                )

    return jsonify({
        "mensaje": "Item eliminado correctamente",
        "idcarrito": idcarrito,
        "id_item_carrito": iditem,
        "idproducto": item["id_item_producto"],
        "cantidad_eliminada": item["cantidad"]
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