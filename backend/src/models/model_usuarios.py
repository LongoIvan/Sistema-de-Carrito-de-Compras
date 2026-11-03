from enum import Enum

class Rol(Enum):
    Admin = "Administrador"
    Cliente = "Cliente"

class Usuario():
    def __init__(self,idusuario:int,nombre:str,mail:str,contrasenia:str,rol:Rol):
        self.idusuario = idusuario
        self.nombre = nombre
        self.mail = mail
        self.contrasenia = contrasenia
        self.rol = rol
        