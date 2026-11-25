# Librerías de Python
from contextlib import closing

# Flask
from flask import Blueprint, jsonify, request, current_app

# Base de datos
from backend.src.database.database import get_connection

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
                    SELECT idproducto, nombre, precio, stock, activo
                    FROM producto
                    WHERE idproducto = %s
                    """,
                    (idproducto,)
                )

                producto = cursor.fetchone()

                if producto is None:
                    return jsonify({"error": "Producto no encontrado"}), 404

                # Validar que el producto este activo
                if not producto["activo"]:
                    return jsonify({
                        "error": "El producto esta desactivado"
                    }), 400

                # 3. Buscar el producto existente en el carrito
                cursor.execute(
                    """
                    SELECT id_item_carrito, cantidad, precio_unitario
                    FROM item_carrito
                    WHERE idcarrito = %s
                    AND id_item_producto = %s
                    """,
                    (idcarrito, idproducto)
                    )

                item_existente = cursor.fetchone()

                cantidad_en_carrito = (
                    item_existente["cantidad"] if item_existente else 0
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
                if item_existente:
                    iditem = item_existente["id_item_carrito"]
                    precio_unitario = item_existente["precio_unitario"]

                    cursor.execute(
                        """
                        UPDATE item_carrito
                        SET cantidad = %s
                        WHERE id_item_carrito = %s
                          AND idcarrito = %s
                        """,
                        (cantidad_total, iditem, idcarrito)
                    )

                    mensaje = "Cantidad del producto actualizada correctamente"
                    codigo_estado = 200

                # 6. Si no existe, crear un nuevo item
                else:
                    precio_unitario = producto["precio"]

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
                            precio_unitario
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
        "precio_unitario": float(precio_unitario)
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
                    SELECT id_item_producto, cantidad
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

                # 3. Consultar el stock y estado del producto
                cursor.execute(
                    """
                    SELECT nombre, stock, activo
                    FROM producto
                    WHERE idproducto = %s
                    """,
                    (item["id_item_producto"],)
                )

                producto = cursor.fetchone()

                if producto is None:
                    return jsonify({"error": "Producto no encontrado"}), 404

                if not producto["activo"]:
                    return jsonify({
                        "error": "El producto esta desactivado"
                    }), 400

                # 4. Calcular la cantidad total del producto
                cantidad_en_carrito = item["cantidad"]
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
                nueva_cantidad = cantidad_total

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