from backend.src.models.model_usuarios import Usuario


#--Devuelve Variables--
def mostrar_idusuario(self):
    return self.idusuario

def mostrar_nombre(self):
    return self.nombre

def mostrar_mail(self):
    return self.mail

def mostrar_rol(self):
    return self.rol


#--Modifica Valores--
def modificar_nombre(self, nuevoNombre:str):
    if type(nuevoNombre) == str and len(nuevoNombre) > 3 and len(nuevoNombre) < 50:
        for i in nuevoNombre:
            #Linea generada por Gemini
            if i == " " or i == "!" or i == '"' or i == "#" or i == "$" or i == "%" or i == "&" or i == "'" or i == "(" or i == ")" or i == "*" or i == "+" or i == "," or i == "-" or i == "." or i == "/" or i == ":" or i == ";" or i == "<" or i == "=" or i == ">" or i == "?" or i == "@" or i == "[" or i == "\\" or i == "]" or i == "^" or i == "_" or i == "`" or i == "{" or i == "|" or i == "}" or i == "~":
                print("--ERROR - Nombre Invalido--")
                return
        self.nombre = nuevoNombre
        print("--Nombre Actualizado")
    else:
        print("--ERROR - Nombre Invalido--")
    

def modificar_mail(self, nuevoMail:str):
    if type(nuevoMail) == str and len(nuevoMail) > 5 and len(nuevoMail) < 50:
        for i in nuevoMail:
            #Linea generada por Gemini
            if i == " " or i == "!" or i == '"' or i == "#" or i == "$" or i == "%" or i == "&" or i == "'" or i == "(" or i == ")" or i == "*" or i == "+" or i == "," or i == "/" or i == ":" or i == ";" or i == "<" or i == "=" or i == ">" or i == "?" or i == "[" or i == "\\" or i == "]" or i == "^" or i == "`" or i == "{" or i == "|" or i == "}" or i == "~":
                print("--ERROR - Email Invalido--")
                return
        self.mail = nuevoMail
        print("--Email Actualizado--")
    else:
        print("--ERROR - Email Invalido--")

def modificar_contrasenia(self, nuevaContra:str):
    if type(nuevaContra) == str and len(nuevaContra) < 8:
        letraupper = False
        for i in nuevaContra:
            if i.isupper():
                letraupper = True
        if letraupper:
            self.contrasenia = nuevaContra
            print("--Contraseña Actualizada--")
        else:
            print("--ERROR --")
            print("--La contraseña no tiene un caracter Upper--")
            return
    else:
        print("--ERROR - Contraseña Invalida--")