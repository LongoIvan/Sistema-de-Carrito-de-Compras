from backend.src.models.model_productos import Producto

def __str__(self):
    return (f"""
    Id_producto: {self.idproducto}
    Nombre: {self.nombre}
    Precio: {self.precio}
    Stock: {self.stock}
    Categoria: {self.categoria}
    Fecha: {self.fecha}
    Activo: {self.activo}
    Descripcion: {self.descripcion}
""")
