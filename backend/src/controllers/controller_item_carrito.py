from backend.src.models.model_item_carrito import ItemCarrito


#Devolver datos

def mostrar_id(item_carrito:ItemCarrito):
    return item_carrito.id_item_carrito

def mostrar_id_producto(item_carrito:ItemCarrito):
    return item_carrito.id_item_producto

def mostrar_cantidad(item_carrito:ItemCarrito):
    return item_carrito.cantidad

def mostar_precio(item_carrito:ItemCarrito):
    return item_carrito.precio_unitario

#Metodos

def modificar_cantidad(item_carrito:ItemCarrito):
    def aumentar(num:int):
        if num.isdigit():
            item_carrito.cantidad += num
        else:
            print("--ERROR - Valor Invalido--")
            return

    def disminuir(num:int):
        if num.isdigit():
            if num > item_carrito.cantidad:
                item_carrito.cantidad = 1
            else:
                item_carrito.cantidad -= num
        else:
            print("--ERROR - Valor Invalido--")
            return

def calcular_subtotal(item_carrito:ItemCarrito):
    sub_total = 0
    sub_total = item_carrito.cantidad * item_carrito.precio_unitario
    return sub_total