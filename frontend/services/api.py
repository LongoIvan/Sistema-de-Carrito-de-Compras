import os
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")
TIMEOUT = 10


def _procesar_respuesta(response: requests.Response) -> dict:
    try:
        data = response.json()
    except ValueError:
        data = {"mensaje": response.text}

    return {
        "ok": response.ok,
        "status_code": response.status_code,
        "data": data,
    }


def _request(method: str, endpoint: str, json_body: dict | None = None) -> dict:
    url = f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    try:
        response = requests.request(
            method=method,
            url=url,
            json=json_body,
            timeout=TIMEOUT,
        )
        return _procesar_respuesta(response)
    except requests.RequestException as exc:
        return {
            "ok": False,
            "status_code": 0,
            "data": {"error": f"No se pudo conectar con la API: {exc}"},
        }


# =========================================================
# CONTROLADOR DE USUARIOS 
# =========================================================

def crear_usuario(nombre: str, mail: str, contrasenia: str) -> dict:
    payload = {
        "nombre": nombre,
        "mail": mail,
        "contrasenia": contrasenia,
    }
    return _request("POST", "/usuario", json_body=payload)


def obtener_usuario(id_usuario: int) -> dict:
    return _request("GET", f"/usuario/{id_usuario}")


def obtener_usuario_completo(id_usuario: int) -> dict:
    return _request("GET", f"/usuario/{id_usuario}/completo")


def obtener_usuario_nombre(id_usuario: int) -> dict:
    return _request("GET", f"/usuario/{id_usuario}/nombre")


def obtener_usuario_mail(id_usuario: int) -> dict:
    return _request("GET", f"/usuario/{id_usuario}/mail")


def obtener_usuario_rol(id_usuario: int) -> dict:
    return _request("GET", f"/usuario/{id_usuario}/rol")


def actualizar_usuario_nombre(id_usuario: int, nombre: str) -> dict:
    return _request("PATCH", f"/usuario/{id_usuario}/nombre", json_body={"nombre": nombre})


def actualizar_usuario_mail(id_usuario: int, mail: str) -> dict:
    return _request("PATCH", f"/usuario/{id_usuario}/mail", json_body={"mail": mail})


def actualizar_usuario_contrasenia(id_usuario: int, contrasenia: str) -> dict:
    return _request("PATCH", f"/usuario/{id_usuario}/contrasenia", json_body={"contrasenia": contrasenia})


def eliminar_usuario(id_usuario: int) -> dict:
    return _request("DELETE", f"/usuario/{id_usuario}")


# =========================================================
# CONTROLADOR DE PRODUCTOS 
# =========================================================

def agregar_stock_producto(id_producto: int, stock: int) -> dict:
    return _request("PATCH", f"/productos/{id_producto}/stock/agregar", json_body={"stock": stock})


def quitar_stock_producto(id_producto: int, stock: int) -> dict:
    return _request("PATCH", f"/productos/{id_producto}/stock/quitar", json_body={"stock": stock})




def listar_productos() -> dict:
    return _request("GET", "/productos")


def obtener_producto(id_producto: int) -> dict:
    return _request("GET", f"/productos/{id_producto}")


def crear_producto(payload: dict) -> dict:
    return _request("POST", "/productos", json_body=payload)


def actualizar_producto(id_producto: int, payload: dict) -> dict:
    return _request("PATCH", f"/productos/{id_producto}", json_body=payload)


def eliminar_producto(id_producto: int) -> dict:
    return _request("DELETE", f"/productos/{id_producto}")


# =========================================================
# CONTROLADOR DE CARRITOS 
# =========================================================

def crear_carrito(id_usuario: int) -> dict:
    return _request("POST", "/carritos", json_body={"idusuario": id_usuario})


def obtener_items_carrito(id_carrito: int) -> dict:
    return _request("GET", f"/carritos/{id_carrito}/items")


def finalizar_carrito(id_carrito: int) -> dict:
    return _request("PATCH", f"/carritos/{id_carrito}/finalizar")


def cancelar_carrito(id_carrito: int) -> dict:
    return _request("PATCH", f"/carritos/{id_carrito}/cancelar")


# =========================================================
# CONTROLADOR DE ÍTEMS DEL CARRITO 
# =========================================================

def agregar_item_carrito(id_carrito: int, id_producto: int, cantidad: int) -> dict:
    payload = {
        "idproducto": id_producto,
        "cantidad": cantidad,
    }
    return _request("POST", f"/carritos/{id_carrito}/items", json_body=payload)


# --- Confirmar rutas exactas y claves JSON de aumentar/disminuir con `flask routes` ---

def aumentar_cantidad_item(id_carrito: int, id_producto: int, cantidad: int = 1) -> dict:
    return _request(
        "PATCH",
        f"/carritos/{id_carrito}/items/{id_producto}/aumentar",
        json_body={"cantidad": cantidad},
    )


def disminuir_cantidad_item(id_carrito: int, id_producto: int, cantidad: int = 1) -> dict:
    return _request(
        "PATCH",
        f"/carritos/{id_carrito}/items/{id_producto}/disminuir",
        json_body={"cantidad": cantidad},
    )