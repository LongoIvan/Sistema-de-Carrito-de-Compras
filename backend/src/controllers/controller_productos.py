# from flask import Blueprint, jsonify

# from backend.src.database.database import fetch_all

from backend.src.models.model_productos import Producto, Categoria

producto1 = Producto(
    1, "Mouse Logitech", 15000.0,
    list(Categoria)[0], "Mouse inalámbrico"
)

producto2 = Producto(
    2, "Teclado Redragon", 35000.0,
    list(Categoria)[0], "Teclado mecánico RGB"
)

producto3 = Producto(
    3, "Monitor Samsung", 180000.0,
    list(Categoria)[0], "Monitor LED de 24 pulgadas"
)

productos = [producto1, producto2, producto3]


# productos_bp = Blueprint("productos", __name__)


# @productos_bp.get("/api/productos")
# def listar_productos():
#     productos = fetch_all(
#         """
#         SELECT idproducto, nombre, precio, stock, categoria, fecha, activo, descripcion
#         FROM producto
#         """
#     )
#     for producto in productos:
#         producto["fecha"] = producto["fecha"].isoformat()
#         producto["activo"] = bool(producto["activo"])

#     return jsonify(productos)


def mostrar_nombre (producto):
    print(f"Nombre: {producto.nombre}")

def mostrar_precio (producto):
    print(f"Precio: ${producto.precio}")

def mostrar_stock (producto):
    print(f"Stock: {producto.stock}")

def mostrar_categoria (producto):
    print (f"Categoria: {producto.categoria}")

def mostrar_fecha (producto):
    print (f"Fecha: {producto.fecha}")

def mostrar_descripcion (producto):
    print (f"Descripcion: {producto.descripcion}")

def agregar_productos(producto):
    for product in productos:
        if product.idproducto == producto.idproducto:
            print ("Este producto ya existe")
            return
    productos.append(producto)
    print (f"El producto {producto.nombre} se agrego correctamente")

def modificar_precio (producto, precio):
    for product in productos:
        if product.idproducto == producto.idproducto:
            if precio < 0:
                print ("El precio no puede ser negativo")
                return
            product.precio = precio
            print (f"El precio a sido modificado correctamente")
            return
        
    print ("El producto no se encuentra listado")

def modificar_stock (producto, stock):
    for product in productos:
        if product.idproducto == producto.idproducto:
            if stock < 0:
                print ("El stock no puede ser negativo")
                return
            elif stock > 0:
                product.activo = True
                product.stock = stock
                print ("El stock a sido modificado correctamente")
                return
            else:
                product.stock = stock
                product.activo = False
                print ("Stock modificado a inactivo")
                return
    print ("El producto no se encuentra listado")

def agregar_stock (producto, stock):
    for product in productos:
        if product.idproducto == producto.idproducto:
            if stock <= 0:
                print ("Usted no puede poner numeros negativos o 0")
                return
            product.stock += stock
            product.activo = True
            print ("El stock a sido modificado correctamente")
            return
            
    print ("El producto no se encuentra listado")

def quitar_stock (producto, stock):
    for product in productos:
        if product.idproducto == producto.idproducto:
            if stock <= 0:
                print ("Usted no puede poner numeros negativos o 0")
                return
            elif product.stock < stock:
                print ("No hay suficiente cantidad de producto para sacar")
                return
            product.stock -= stock
            if product.stock == 0:
                product.activo = False
            else:
                product.activo = True
            print ("El stock a sido modificado correctamente")
            return
    print ("El producto no se encuentra listado")

def modificar_nombre(producto,nombre):
    for product in productos:
        if product.idproducto == producto.idproducto:
            if not isinstance(nombre,str):
                print("Por favor ingresar el nombre del producto correctamente")
                return
            nombre = nombre.strip()
            if not nombre:
                print ("Por favor ingrese el nombre del producto correctamente(no vacio)")
                return
            product.nombre = nombre
            print ("El nombre del producto fue modificado correctamente!")
            return
    print ("El producto no se encuentra listado")

def modificar_descripcion(producto,descripcion):
    for product in productos:
        if product.idproducto == producto.idproducto:
            if not isinstance(descripcion,str):
                print("Por favor ingresar la descripcion del producto correctamente")
                return
            descripcion = descripcion.strip()
            if not descripcion:
                print ("Por favor ingresar la descripcion del producto correctamente(no vacio)")
                return
            product.descripcion = descripcion
            print ("La descripcion del producto fue modificado correctamente!")
            return
    print ("El producto no se encuentra listado")

def modificar_categoria (producto,categoria):
    for product in productos:
        if product.idproducto == producto.idproducto:
            if not isinstance (categoria, Categoria):
                print ("Por favor introduzca una categoria valida")
                return
            product.categoria = categoria
            print ("La categoria se modifico correctamente")
            return
    print ("El producto no se encuentra listado")

def eliminar_producto(producto):
    for product in productos:
        if product.idproducto == producto.idproducto:
            productos.remove(product)
            print ("El producto fue eliminado correctamente de la lista")
            return
    print ("El producto no se encuentra listado")
