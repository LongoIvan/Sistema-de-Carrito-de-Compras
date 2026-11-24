from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from backend.src.database.database import execute_query, fetch_all
from psycopg2.errors import UniqueViolation, ForeignKeyViolation, RestrictViolation


usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/api/usuario/<int:id>/completo", methods=["GET"])
def mostrar_usuario_completo(id):
    consulta = """
        SELECT idusuario, nombre, mail, rol
        FROM usuario
        WHERE idusuario = %s
    """

    usuarios = fetch_all(consulta, (id,))

    if not usuarios:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(usuarios[0]), 200


@usuarios_bp.route("/api/usuario/<int:id>", methods=["GET"])
def mostrar_idusuario(id):
    consulta = """
        SELECT idusuario
        FROM usuario
        WHERE idusuario = %s
    """

    usuarios = fetch_all(consulta, (id,))

    if not usuarios:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(usuarios[0]), 200

@usuarios_bp.route("/api/usuario/<int:id>/nombre", methods=["GET"])
def mostrar_nombre(id):
    consulta = """
        SELECT nombre
        FROM usuario
        WHERE idusuario = %s
    """

    usuarios = fetch_all(consulta, (id,))

    if not usuarios:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(usuarios[0]), 200


@usuarios_bp.route("/api/usuario/<int:id>/mail", methods=["GET"])
def mostrar_mail(id):
    consulta = """
        SELECT mail
        FROM usuario
        WHERE idusuario = %s
    """

    usuarios = fetch_all(consulta, (id,))

    if not usuarios:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(usuarios[0]), 200


@usuarios_bp.route("/api/usuario/<int:id>/rol", methods=["GET"])
def mostrar_rol(id):
    consulta = """
        SELECT rol
        FROM usuario
        WHERE idusuario = %s
    """

    usuarios = fetch_all(consulta, (id,))

    if not usuarios:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(usuarios[0]), 200


#--Modifica Valores--
@usuarios_bp.route("/api/usuario/<int:id>/nombre", methods=["PATCH"])
#@usuarios_bp.route("/api/usuario/<int:id>", methods=["PATCH"])
def modificar_nombre(id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "nombre" not in datos:
        return jsonify({"error": "Datos incompletos"}), 400

    nuevoNombre = datos["nombre"]

    if type(nuevoNombre) is not str:
        return jsonify({"error": "El nombre debe ser un texto"}), 400

    nuevoNombre = nuevoNombre.strip()

    if len(nuevoNombre) <= 3 or len(nuevoNombre) >= 50:
        return jsonify({"error": "El nombre debe tener entre 4 y 49 caracteres"}), 400

    if not nuevoNombre.replace(" ", "").isalpha():
        return jsonify({"error": "El nombre contiene caracteres invalidos"}), 400

    consulta = "UPDATE usuario SET nombre = %s WHERE idusuario = %s"

    filas = execute_query(consulta, (nuevoNombre, id))

    if filas == 0:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({"mensaje": "Nombre actualizado", "nombre": nuevoNombre}), 200

    
@usuarios_bp.route("/api/usuario/<int:id>/mail", methods=["PATCH"])
def modificar_mail(id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "mail" not in datos:
        return jsonify({"error": "Datos incompletos"}), 400

    nuevoMail = datos["mail"]

    if type(nuevoMail) is not str:
        return jsonify({"error": "El mail debe ser un texto"}), 400

    nuevoMail = nuevoMail.strip().lower()

    if len(nuevoMail) <= 5 or len(nuevoMail) >= 50:
        return jsonify({"error": "El mail debe tener entre 6 y 49 caracteres"}), 400

    if nuevoMail.count("@") != 1 or any(c.isspace() for c in nuevoMail):
        return jsonify({"error": "Formato de mail invalido"}), 400

    parte_local, dominio = nuevoMail.split("@")

    if not parte_local or "." not in dominio or dominio.startswith(".") or dominio.endswith("."):
        return jsonify({"error": "Formato de mail invalido"}), 400

    consulta = """
        UPDATE usuario
        SET mail = %s
        WHERE idusuario = %s
    """

    try:
        filas = execute_query(consulta, (nuevoMail, id))

    except UniqueViolation:
        return jsonify({"error": "El mail ya esta registrado"}), 409

    if filas == 0:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "mensaje": "Mail actualizado",
        "mail": nuevoMail
    }), 200

@usuarios_bp.route("/api/usuario/<int:id>/contrasenia", methods=["PATCH"])
#@usuarios_bp.route("/api/usuario/<int:id>", methods=["PATCH"])
def modificar_contrasenia(id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "contrasenia" not in datos:
        return jsonify({"error": "Datos incompletos"}), 400

    nuevaContra = datos["contrasenia"]

    if type(nuevaContra) is not str:
        return jsonify({"error": "La contraseña debe ser un texto"}), 400

    if len(nuevaContra) < 8:
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400

    letraupper = False

    for i in nuevaContra:
        if i.isupper():
            letraupper = True
            break

    if not letraupper:
        return jsonify({"error": "La contraseña debe contener una mayuscula"}), 400

    contrasenia_hash = generate_password_hash(nuevaContra)

    consulta = "UPDATE usuario SET contrasenia = %s WHERE idusuario = %s"
    filas = execute_query(consulta, (contrasenia_hash, id))

    if filas == 0:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({"mensaje": "Contraseña actualizada"}), 200

@usuarios_bp.route("/api/usuario", methods=["POST"])
def agregar_usuario():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({"error": "JSON invalido"}), 400

    campos = ["nombre", "mail", "contrasenia"]

    for campo in campos:
        if campo not in datos:
            return jsonify({"error": f"Falta el campo {campo}"}), 400

    nombre = datos["nombre"]
    mail = datos["mail"]
    contrasenia = datos["contrasenia"]

    # Validar nombre
    if type(nombre) is not str:
        return jsonify({"error": "Nombre invalido"}), 400

    nombre = nombre.strip()

    if len(nombre) <= 3 or len(nombre) >= 50:
        return jsonify({"error": "Nombre invalido"}), 400

    if not nombre.replace(" ", "").isalpha():
        return jsonify({"error": "Nombre invalido"}), 400

    # Validar mail
    if type(mail) is not str:
        return jsonify({"error": "Mail invalido"}), 400

    mail = mail.strip().lower()

    if len(mail) <= 5 or len(mail) >= 50:
        return jsonify({"error": "Mail invalido"}), 400

    if mail.count("@") != 1 or any(c.isspace() for c in mail):
        return jsonify({"error": "Mail invalido"}), 400

    parte_local, dominio = mail.split("@")

    if not parte_local or "." not in dominio or dominio.startswith(".") or dominio.endswith("."):
        return jsonify({"error": "Mail invalido"}), 400

    # Validar contraseña
    if type(contrasenia) is not str or len(contrasenia) < 8:
        return jsonify({"error": "Contraseña invalida"}), 400

    if not any(letra.isupper() for letra in contrasenia):
        return jsonify({"error": "La contraseña necesita una mayuscula"}), 400

    # Proteger contraseña
    contrasenia_hash = generate_password_hash(contrasenia)

    # Insertar usuario
    consulta = """
        INSERT INTO usuario (nombre, mail, contrasenia, rol)
        VALUES (%s, %s, %s, %s)
    """

    try:
        execute_query(consulta, (nombre, mail, contrasenia_hash, "Cliente"))

    except UniqueViolation:
        return jsonify({"error": "El mail ya esta registrado"}), 409

    return jsonify({
        "mensaje": "Usuario creado correctamente",
        "nombre": nombre,
        "mail": mail
    }), 201

@usuarios_bp.route("/api/usuario/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):

    consulta = "DELETE FROM usuario WHERE idusuario = %s"

    try:
        filas = execute_query(consulta, (id,))

    except (ForeignKeyViolation, RestrictViolation):
        return jsonify({
            "error": "No se puede eliminar un usuario con carritos asociados"
        }), 409

    if filas == 0:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "mensaje": "Usuario eliminado correctamente"
    }), 200

@usuarios_bp.route("/api/usuario/login", methods=["POST"])
def login_usuario():

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({"error": "JSON invalido"}), 400

    campos = ["mail", "contrasenia"]

    for campo in campos:
        if campo not in datos:
            return jsonify({"error": f"Falta el campo {campo}"}), 400

    mail = datos["mail"]
    contrasenia = datos["contrasenia"]

    if type(mail) is not str or type(contrasenia) is not str:
        return jsonify({"error": "Credenciales invalidas"}), 400

    mail = mail.strip().lower()

    if not mail or not contrasenia:
        return jsonify({"error": "Credenciales invalidas"}), 400
        consulta = """
        SELECT idusuario, nombre, mail, contrasenia, rol
        FROM usuario
        WHERE mail = %s
    """

    resultado = fetch_all(consulta, (mail,))

    if not resultado:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    usuario = resultado[0]

    if not check_password_hash(usuario["contrasenia"], contrasenia):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    return jsonify({
        "mensaje": "Inicio de sesion correcto",
        "idusuario": usuario["idusuario"],
        "nombre": usuario["nombre"],
        "mail": usuario["mail"],
        "rol": usuario["rol"]
    }), 200