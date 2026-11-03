from backend.src.models.model_usuarios import Usuario

def __str__(self):
    return (f"""
        Id_usuario: {self.idusuario}
        Nombre: {self.nombre}
        Mail: {self.mail}
        Rol: {self.rol}
""")