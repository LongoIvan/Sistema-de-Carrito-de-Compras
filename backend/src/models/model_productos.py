from datetime import date
from enum import Enum

class Categoria(Enum):
    Electronico = "Electronico"
    Comida = "Comida"

class Producto:
    def __init__(self,idproducto:int,nombre:str,precio:float,categoria:Categoria,descripcion:str):
        self.idproducto = idproducto
        self.nombre = nombre
        self.precio = precio
        self.stock = 1
        self.categoria = categoria
        self.fecha = date.today()
        self.activo = True
        self.descripcion = descripcion

