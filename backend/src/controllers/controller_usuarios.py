from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from backend.src.database.database import execute_query, fetch_all

usuarios_bp = Blueprint("usuarios", __name__)



@usuarios_bp.route("/usuario/<int:id>", methods=["GET"])
def mostrar_idusuario(id):
    consulta = "SELECT idusuario FROM usuario"
    usuarios = fetch_all(consulta)

    for usuario in usuarios:
        if usuario["idusuario"] == id:
            return jsonify({"idusuario": usuario["idusuario"]}), 200

    return jsonify({"error": "Usuario no encontrado"}), 404

@usuarios_bp.route("/usuario/<int:id>/nombre", methods=["GET"])
def mostrar_nombre(id):
    consulta = "SELECT idusuario, nombre FROM usuario"
    usuarios = fetch_all(consulta)

    for usuario in usuarios:
        if usuario["idusuario"] == id:
            return jsonify({"nombre": usuario["nombre"]}), 200

    return jsonify({"error": "Usuario no encontrado"}), 404


@usuarios_bp.route("/usuario/<int:id>/mail", methods=["GET"])
def mostrar_mail(id):
    consulta = "SELECT idusuario, mail FROM usuario"
    usuarios = fetch_all(consulta)

    for usuario in usuarios:
        if usuario["idusuario"] == id:
            return jsonify({"mail": usuario["mail"]}), 200

    return jsonify({"error": "Usuario no encontrado"}), 404


@usuarios_bp.route("/usuario/<int:id>/rol", methods=["GET"])
def mostrar_rol(id):
    consulta = "SELECT idusuario, rol FROM usuario"
    usuarios = fetch_all(consulta)

    for usuario in usuarios:
        if usuario["idusuario"] == id:
            return jsonify({"rol": usuario["rol"]}), 200

    return jsonify({"error": "Usuario no encontrado"}), 404


#--Modifica Valores--
@usuarios_bp.route("/usuario/<int:id>/nombre", methods=["PATCH"])
#@usuarios_bp.route("/usuario/<int:id>", methods=["PATCH"])
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

    
@usuarios_bp.route("/usuario/<int:id>/mail", methods=["PATCH"])
#@usuarios_bp.route("/usuario/<int:id>", methods=["PATCH"])
def modificar_mail(id):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "mail" not in datos:
        return jsonify({"error": "Datos incompletos"}), 400

    nuevoMail = datos["mail"]

    if type(nuevoMail) is not str:
        return jsonify({"error": "El mail debe ser un texto"}), 400

    nuevoMail = nuevoMail.strip()

    if len(nuevoMail) <= 5 or len(nuevoMail) >= 50:
        return jsonify({"error": "El mail debe tener entre 6 y 49 caracteres"}), 400

    if nuevoMail.count("@") != 1 or " " in nuevoMail:
        return jsonify({"error": "Formato de mail invalido"}), 400

    parte_local, dominio = nuevoMail.split("@")

    if not parte_local or "." not in dominio or dominio.startswith(".") or dominio.endswith("."):
        return jsonify({"error": "Formato de mail invalido"}), 400

    consulta = "SELECT idusuario, mail FROM usuario"
    usuarios = fetch_all(consulta)

    for usuario in usuarios:
        if usuario["mail"].lower() == nuevoMail.lower() and usuario["idusuario"] != id:
            return jsonify({"error": "El mail ya esta registrado"}), 409

    consulta = "UPDATE usuario SET mail = %s WHERE idusuario = %s"
    filas = execute_query(consulta, (nuevoMail, id))

    if filas == 0:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({"mensaje": "Mail actualizado", "mail": nuevoMail}), 200

@usuarios_bp.route("/usuario/<int:id>/contrasenia", methods=["PATCH"])
#@usuarios_bp.route("/usuario/<int:id>", methods=["PATCH"])
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

@usuarios_bp.route("/usuario", methods=["POST"])
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

    mail = mail.strip()

    if len(mail) <= 5 or len(mail) >= 50:
        return jsonify({"error": "Mail invalido"}), 400

    if mail.count("@") != 1 or " " in mail:
        return jsonify({"error": "Mail invalido"}), 400

    parte_local, dominio = mail.split("@")

    if not parte_local or "." not in dominio or dominio.startswith(".") or dominio.endswith("."):
        return jsonify({"error": "Mail invalido"}), 400

    # Comprobar si el mail ya existe
    usuarios = fetch_all("SELECT mail FROM usuario")

    for usuario in usuarios:
        if usuario["mail"].lower() == mail.lower():
            return jsonify({"error": "El mail ya esta registrado"}), 409

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

    execute_query(consulta, (nombre, mail, contrasenia_hash, "Cliente"))

    return jsonify({
        "mensaje": "Usuario creado correctamente",
        "nombre": nombre,
        "mail": mail
    }), 201

@usuarios_bp.route("/usuario/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):

    consulta = "DELETE FROM usuario WHERE idusuario = %s"

    filas = execute_query(consulta, (id,))

    if filas == 0:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200