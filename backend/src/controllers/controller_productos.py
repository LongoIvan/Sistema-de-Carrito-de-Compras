from flask import Blueprint, jsonify

from backend.src.database.database import fetch_all


productos_bp = Blueprint("productos", __name__)


@productos_bp.get("/api/productos")
def listar_productos():
    productos = fetch_all(
        """
        SELECT idproducto, nombre, precio, stock, categoria, fecha, activo, descripcion
        FROM producto
        """
    )
    for producto in productos:
        producto["fecha"] = producto["fecha"].isoformat()
        producto["activo"] = bool(producto["activo"])

    return jsonify(productos)
