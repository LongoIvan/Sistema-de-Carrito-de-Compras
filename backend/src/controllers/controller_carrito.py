from flask import Blueprint, jsonify

from backend.src.database.database import fetch_all


carritos_bp = Blueprint("carritos", __name__)


@carritos_bp.get("/api/carritos")
def listar_carritos():
    carritos = fetch_all(
        """
        SELECT
            c.idcarrito,
            c.idusuario,
            c.fecha,
            c.estado,
            COALESCE(
                json_agg(
                    json_build_object(
                        'nombre_producto', p.nombre,  -- Reemplazamos el ID por el nombre del producto
                        'cantidad', i.cantidad,
                        'precio_unitario', i.precio_unitario
                    )
                    ORDER BY i.id_item_carrito
                ) FILTER (WHERE i.id_item_carrito IS NOT NULL),
                '[]'::json
            ) AS item
        FROM carrito AS c
        LEFT JOIN item_carrito AS i ON i.idcarrito = c.idcarrito
        LEFT JOIN producto AS p ON p.idproducto = i.id_item_producto  -- Hacemos el JOIN con la tabla producto
        GROUP BY c.idcarrito, c.idusuario, c.fecha, c.estado
        ORDER BY c.idcarrito
        """
    )
    for carrito in carritos:
        carrito["fecha"] = carrito["fecha"].isoformat()

    return jsonify(carritos)
