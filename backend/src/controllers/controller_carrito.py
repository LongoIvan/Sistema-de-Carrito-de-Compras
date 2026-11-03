from backend.src.models.model_carrito import Carrito

def __str__(self):
    return (f"""
        Id_carrito: {self.idcarrito}
        Id_usuario: {self.idusuario}  
        Fecha_creado: {self.fecha}
        Estado: {self.estado}
        Producto: {self.item}
    """)
