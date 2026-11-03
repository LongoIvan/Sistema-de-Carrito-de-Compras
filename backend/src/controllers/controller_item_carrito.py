from backend.src.models.model_item_carrito import ItemCarrito

def __str__(self):
        return(f"""
            Id Item Carrito: {self.id_item_carrito}
            Id Item Producto: {self.id_item_producto}
            Cantidad: {self.cantidad}
            Precio Unitario: {self.precio_unitario}
""")
