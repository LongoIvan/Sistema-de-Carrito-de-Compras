from flask import Blueprint, jsonify

from backend.src.database.database import fetch_all


items_carrito_bp = Blueprint("items_carrito", __name__)


@items_carrito_bp.get("/api/items-carrito")
def listar_items_carrito():
    return jsonify(
        fetch_all(
            """
            SELECT id_item_carrito, idcarrito, id_item_producto, cantidad, precio_unitario
            FROM item_carrito
            """
        )
    )
