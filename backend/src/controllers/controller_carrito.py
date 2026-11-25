# Librerías de Python
from contextlib import closing

# Flask
from flask import Blueprint, jsonify, request, current_app

# Base de datos
from backend.src.database.database import (
    fetch_all,
    execute_query_returning,
    get_connection
)

carritos_bp = Blueprint("carritos", __name__)


@carritos_bp.route("/api/carritos", methods=["POST"])
def crear_carrito():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "idusuario" not in datos:
        return jsonify({"error": "Datos incompletos"}), 400

    idusuario = datos["idusuario"]

    if type(idusuario) is not int or idusuario <= 0:
        return jsonify({"error": "ID de usuario invalido"}), 400

    usuarios = fetch_all(
        "SELECT idusuario FROM usuario WHERE idusuario = %s",
        (idusuario,)
    )

    if not usuarios:
        return jsonify({"error": "Usuario no encontrado"}), 404

    consulta = """
        INSERT INTO carrito (idusuario, fecha, estado)
        VALUES (%s, CURRENT_DATE, %s)
        RETURNING idcarrito
    """

    resultado = execute_query_returning(consulta, (idusuario, "Pendiente"))

    return jsonify({
        "mensaje": "Carrito creado correctamente",
        "idcarrito": resultado["idcarrito"],
        "idusuario": idusuario,
        "estado": "Pendiente"
    }), 201


@carritos_bp.route("/api/carritos/<int:id>", methods=["GET"])
def consultar_carrito(id):
    carritos = fetch_all(
        "SELECT * FROM carrito WHERE idcarrito = %s",
        (id,)
    )

    if not carritos:
        return jsonify({"error": "Carrito no encontrado"}), 404

    carrito = carritos[0]

    return jsonify(carrito), 200



@carritos_bp.route("/api/carritos/<int:id>/finalizar", methods=["PATCH"])
def finalizar_carrito(id):

    with closing(get_connection(current_app.config["DATABASE_URL"])) as connection:
        with connection:
            with connection.cursor() as cursor:

                # 1. Buscar y bloquear el carrito
                cursor.execute(
                    """
                    SELECT estado
                    FROM carrito
                    WHERE idcarrito = %s
                    FOR UPDATE
                    """,
                    (id,)
                )

                carrito = cursor.fetchone()

                if carrito is None:
                    return jsonify({"error": "Carrito no encontrado"}), 404

                if carrito["estado"] != "Pendiente":
                    return jsonify({"error": "El carrito no esta pendiente"}), 400

                # 2. Obtener los productos del carrito
                cursor.execute(
                    """
                    SELECT
                        i.id_item_carrito,
                        i.id_item_producto AS idproducto,
                        p.nombre,
                        i.cantidad
                    FROM item_carrito AS i
                    JOIN producto AS p
                        ON p.idproducto = i.id_item_producto
                    WHERE i.idcarrito = %s
                    ORDER BY i.id_item_producto, i.id_item_carrito
                    """,
                    (id,)
                )

                items = cursor.fetchall()

                if not items:
                    return jsonify({"error": "El carrito esta vacio"}), 400

                # 3. Agrupar cantidades por producto
                cantidades = {}

                for item in items:
                    idproducto = item["idproducto"]

                    if idproducto not in cantidades:
                        cantidades[idproducto] = 0

                    cantidades[idproducto] += item["cantidad"]

                # 4. Consultar y bloquear los productos
                productos = {}

                for idproducto in sorted(cantidades):
                    cursor.execute(
                        """
                        SELECT nombre, stock, activo
                        FROM producto
                        WHERE idproducto = %s
                        FOR UPDATE
                        """,
                        (idproducto,)
                    )

                    producto = cursor.fetchone()
                    productos[idproducto] = producto

                # 5. Detectar productos desactivados o sin stock suficiente
                productos_corregidos = []

                for idproducto, cantidad_solicitada in cantidades.items():

                    producto = productos[idproducto]

                    # 5.1. Eliminar productos desactivados
                    if not producto["activo"]:

                        cursor.execute(
                            """
                            DELETE FROM item_carrito
                            WHERE idcarrito = %s
                              AND id_item_producto = %s
                            """,
                            (id, idproducto)
                        )

                        productos_corregidos.append({
                            "idproducto": idproducto,
                            "nombre": producto["nombre"],
                            "cantidad_solicitada": cantidad_solicitada,
                            "cantidad_disponible": 0,
                            "accion": "eliminado",
                            "motivo": "Producto desactivado"
                        })

                        continue

                    # 5.2. Comprobar el stock disponible
                    stock_disponible = producto["stock"]

                    if cantidad_solicitada <= stock_disponible:
                        continue

                    restante = stock_disponible

                    for item in items:

                        if item["idproducto"] != idproducto:
                            continue

                        nueva_cantidad = min(item["cantidad"], restante)
                        restante -= nueva_cantidad

                        if nueva_cantidad == 0:
                            cursor.execute(
                                """
                                DELETE FROM item_carrito
                                WHERE id_item_carrito = %s
                                """,
                                (item["id_item_carrito"],)
                            )
                        else:
                            cursor.execute(
                                """
                                UPDATE item_carrito
                                SET cantidad = %s
                                WHERE id_item_carrito = %s
                                """,
                                (nueva_cantidad, item["id_item_carrito"])
                            )

                    productos_corregidos.append({
                        "idproducto": idproducto,
                        "nombre": producto["nombre"],
                        "cantidad_solicitada": cantidad_solicitada,
                        "cantidad_disponible": stock_disponible,
                        "accion": (
                            "eliminado"
                            if stock_disponible == 0
                            else "cantidad_reducida"
                        ),
                        "motivo": "Stock insuficiente"
                    })

                # 6. Si hubo correcciones, rechazar la compra
                if productos_corregidos:
                    return jsonify({
                        "mensaje": "Compra rechazada por productos no disponibles",
                        "idcarrito": id,
                        "estado": "Pendiente",
                        "productos_corregidos": productos_corregidos
                    }), 409

                # 7. Descontar stock y actualizar estado activo
                for idproducto, cantidad in cantidades.items():
                    cursor.execute(
                        """
                        UPDATE producto
                        SET
                            stock = stock - %s,
                            activo = (stock - %s) > 0
                        WHERE idproducto = %s
                        """,
                        (cantidad, cantidad, idproducto)
                    )

                # 8. Finalizar el carrito
                cursor.execute(
                    """
                    UPDATE carrito
                    SET estado = %s
                    WHERE idcarrito = %s
                    """,
                    ("Finalizado", id)
                )

    return jsonify({
        "mensaje": "Compra finalizada correctamente",
        "idcarrito": id,
        "estado": "Finalizado"
    }), 200




@carritos_bp.route("/api/carritos/<int:id>/cancelar", methods=["PATCH"])
def cancelar_carrito(id):

    with closing(get_connection(current_app.config["DATABASE_URL"])) as connection:
        with connection:
            with connection.cursor() as cursor:

                # 1. Buscar y bloquear el carrito
                cursor.execute(
                    """
                    SELECT estado
                    FROM carrito
                    WHERE idcarrito = %s
                    FOR UPDATE
                    """,
                    (id,)
                )

                carrito = cursor.fetchone()

                if carrito is None:
                    return jsonify({"error": "Carrito no encontrado"}), 404

                # 2. Verificar que esté pendiente
                if carrito["estado"] != "Pendiente":
                    return jsonify({
                        "error": "El carrito no esta pendiente"
                    }), 400

                # 3. Cancelar el carrito
                cursor.execute(
                    """
                    UPDATE carrito
                    SET estado = %s
                    WHERE idcarrito = %s
                    """,
                    ("Cancelado", id)
                )

    return jsonify({
        "mensaje": "Carrito cancelado correctamente",
        "idcarrito": id,
        "estado": "Cancelado"
    }), 200



@carritos_bp.route("/api/carritos/<int:id>/total", methods=["GET"])
def calcular_total(id):

    carritos = fetch_all(
        "SELECT idcarrito FROM carrito WHERE idcarrito = %s",
        (id,)
    )

    if not carritos:
        return jsonify({"error": "Carrito no encontrado"}), 404

    consulta = """
        SELECT COALESCE(SUM(cantidad * precio_unitario), 0) AS total
        FROM item_carrito
        WHERE idcarrito = %s
    """

    resultado = fetch_all(consulta, (id,))

    return jsonify({
        "idcarrito": id,
        "total": float(resultado[0]["total"])
    }), 200

@carritos_bp.route("/api/carritos/<int:id>/items", methods=["GET"])
def mostrar_items(id):

    carritos = fetch_all(
        "SELECT idcarrito FROM carrito WHERE idcarrito = %s",
        (id,)
    )

    if not carritos:
        return jsonify({"error": "Carrito no encontrado"}), 404

    consulta = """
        SELECT
            i.id_item_carrito,
            i.id_item_producto AS idproducto,
            p.nombre,
            i.cantidad,
            i.precio_unitario,
            i.cantidad * i.precio_unitario AS subtotal
        FROM item_carrito AS i
        JOIN producto AS p
            ON i.id_item_producto = p.idproducto
        WHERE i.idcarrito = %s
    """

    items = fetch_all(consulta, (id,))

    for item in items:
        item["precio_unitario"] = float(item["precio_unitario"])
        item["subtotal"] = float(item["subtotal"])

    return jsonify({
        "idcarrito": id,
        "items": items
    }), 200