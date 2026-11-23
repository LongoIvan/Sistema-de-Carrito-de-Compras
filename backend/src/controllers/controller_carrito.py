# Librerías de Python
from contextlib import closing

# Flask
from flask import Blueprint, jsonify, request, current_app

# Modelos
from backend.src.models.model_carrito import Carrito, estadocarrito
from backend.src.models.model_item_carrito import ItemCarrito

# Base de datos
from backend.src.database.database import (
    fetch_all,
    execute_query,
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

    usuarios = fetch_all("SELECT idusuario FROM usuario")

    if not any(usuario["idusuario"] == idusuario for usuario in usuarios):
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
    carritos = fetch_all("SELECT * FROM carrito")

    carrito = next(
        (carrito for carrito in carritos if carrito["idcarrito"] == id),
        None
    )

    if carrito is None:
        return jsonify({"error": "Carrito no encontrado"}), 404

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

                # 4. Consultar y bloquear el stock actual
                stocks = {}

                for idproducto in sorted(cantidades):
                    cursor.execute(
                        """
                        SELECT stock
                        FROM producto
                        WHERE idproducto = %s
                        FOR UPDATE
                        """,
                        (idproducto,)
                    )

                    producto = cursor.fetchone()
                    stocks[idproducto] = producto["stock"]

                # 5. Detectar productos con stock insuficiente
                productos_corregidos = []

                for idproducto, cantidad_solicitada in cantidades.items():

                    stock_disponible = stocks[idproducto]

                    if cantidad_solicitada <= stock_disponible:
                        continue

                    # Distribuir el stock disponible entre los items
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
                        "nombre": next(
                            item["nombre"]
                            for item in items
                            if item["idproducto"] == idproducto
                        ),
                        "cantidad_solicitada": cantidad_solicitada,
                        "cantidad_disponible": stock_disponible,
                        "accion": (
                            "eliminado"
                            if stock_disponible == 0
                            else "cantidad_reducida"
                        )
                    })

                # 6. Si hubo correcciones, rechazar la compra
                if productos_corregidos:
                    return jsonify({
                        "mensaje": "Compra rechazada por stock insuficiente",
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

    carritos = fetch_all("SELECT idcarrito FROM carrito")

    if not any(c["idcarrito"] == id for c in carritos):
        return jsonify({"error": "Carrito no encontrado"}), 404

    consulta = f"""
        SELECT COALESCE(SUM(cantidad * precio_unitario), 0) AS total
        FROM item_carrito
        WHERE idcarrito = {id}
    """

    resultado = fetch_all(consulta)

    return jsonify({
        "idcarrito": id,
        "total": float(resultado[0]["total"])
    }), 200

@carritos_bp.route("/api/carritos/<int:id>/items", methods=["GET"])
def mostrar_items(id):

    carritos = fetch_all("SELECT idcarrito FROM carrito")

    if not any(c["idcarrito"] == id for c in carritos):
        return jsonify({"error": "Carrito no encontrado"}), 404

    consulta = f"""
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
        WHERE i.idcarrito = {id}
    """

    items = fetch_all(consulta)

    for item in items:
        item["precio_unitario"] = float(item["precio_unitario"])
        item["subtotal"] = float(item["subtotal"])

    return jsonify({
        "idcarrito": id,
        "items": items
    }), 200



# #Devuelve variables
# def mostrar_idcarrito(self):
#     return self.idcarrito


# def mostrar_id_usuario(self):
#     return self.idusuario

# def mostrar_fecha(self):
#     return self.fecha

# def mostrar_estado(self):
#     return self.estado

# def mostrar_items(self):
#     return self.item

# #Operadores:
# def agregar_item(self, itemagre:ItemCarrito):
#     if type(itemagre) == ItemCarrito and itemagre not in self.item:
#         self.item.append(itemagre)
#         print("--Item Añadido--")
#     else:
#         print("--ERROR - No se pudo añadir el item--")

# def eliminar_item(self, itemelim:ItemCarrito):
#     if type(itemelim) == ItemCarrito and itemelim in self.item:
#         self.item.remove(itemelim)
#         print("--Item Eliminado--")
#     else:
#         print("--ERROR - No se pudo eliminar el item--")

# def calcular_total(self):
#     total_compra = 0
#     for i in self.item:
#         total_compra += (i.cantidad * i.precio_unitario)

#     return total_compra

# def finalizar(self):
#     self.estado = estadocarrito.Finalizado

# def cancelar(self):
#     self.estado = estadocarrito.Cancelado