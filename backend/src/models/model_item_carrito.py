class ItemCarrito:
    def __init__(self,id_item_carrito:int,id_item_producto:int, cantidad:int,precio_unitario:float):
        self.id_item_carrito = id_item_carrito
        self.id_item_producto = id_item_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        