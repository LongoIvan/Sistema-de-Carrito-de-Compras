from datetime import date
from enum import Enum
from backend.src.models.model_item_carrito import ItemCarrito

class estadocarrito(Enum):
    Pendiente = "Pendiente"
    Finalizado = "Finalizado"
    Cancelado = "Cancelado"

class Carrito:
    def __init__(self, idcarrito: int, idusuario: int):
        self.idcarrito = idcarrito
        self.idusuario = idusuario
        self.fecha = date.today()
        self.estado = estadocarrito.Pendiente
        self.item: list[ItemCarrito] = []