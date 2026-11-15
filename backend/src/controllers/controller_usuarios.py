from flask import Blueprint, jsonify

from backend.src.database.database import fetch_all


usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.get("/api/usuarios")
def listar_usuarios():
    return jsonify(fetch_all("SELECT idusuario, nombre, mail, rol FROM usuario"))