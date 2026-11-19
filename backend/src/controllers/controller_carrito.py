from backend.src.models.model_carrito import Carrito
from backend.src.models.model_item_carrito import ItemCarrito
from backend.src.models.model_carrito import estadocarrito


#Devuelve variables
def mostrar_idcarrito(self):
    return self.idcarrito

def mostrar_id_usuario(self):
    return self.idusuario

def mostrar_fecha(self):
    return self.fecha

def mostrar_estado(self):
    return self.estado

def mostrar_items(self):
    return self.item

#Operadores:
def agregar_item(self, itemagre:ItemCarrito):
    if type(itemagre) == ItemCarrito and itemagre not in self.item:
        self.item.append(itemagre)
        print("--Item Añadido--")
    else:
        print("--ERROR - No se pudo añadir el item--")

def eliminar_item(self, itemelim:ItemCarrito):
    if type(itemelim) == ItemCarrito and itemelim in self.item:
        self.item.remove(itemelim)
        print("--Item Eliminado--")
    else:
        print("--ERROR - No se pudo eliminar el item--")

def calcular_total(self):
    total_compra = 0
    for i in self.item:
        total_compra += (i.cantidad * i.precio_unitario)

    return total_compra

def finalizar(self):
    self.estado = estadocarrito.Finalizado

def cancelar(self):
    self.estado = estadocarrito.Cancelado