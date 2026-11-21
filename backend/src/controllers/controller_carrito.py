from backend.src.models.model_carrito import Carrito
from backend.src.models.model_item_carrito import ItemCarrito
from backend.src.models.model_carrito import estadocarrito

from flask import Blueprint, jsonify, request
from backend.src.database.database import fetch_all, execute_query

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
    """

    execute_query(consulta, (idusuario, "Pendiente"))

    return jsonify({
        "mensaje": "Carrito creado correctamente",
        "idusuario": idusuario,
        "estado": "Pendiente"
    }), 201





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