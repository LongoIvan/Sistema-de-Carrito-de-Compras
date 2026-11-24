from contextlib import closing
from werkzeug.security import generate_password_hash
from backend.src.database.database import get_connection
from backend.app import app

def migrar_contrasenias():

    usuarios_actualizados = 0

    with closing(get_connection(app.config["DATABASE_URL"])) as connection:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute("""
                    SELECT idusuario, contrasenia
                    FROM usuario
                    FOR UPDATE
                """)

                usuarios = cursor.fetchall()
                for usuario in usuarios:

                    contrasenia = usuario["contrasenia"]

                    if contrasenia.startswith(("scrypt:", "pbkdf2:")):
                        continue

                    contrasenia_hash = generate_password_hash(contrasenia)

                    cursor.execute("""
                        UPDATE usuario
                        SET contrasenia = %s
                        WHERE idusuario = %s
                    """, (contrasenia_hash, usuario["idusuario"]))

                    usuarios_actualizados += 1
    print(f"Contraseñas migradas correctamente: {usuarios_actualizados}")
    
if __name__ == "__main__":
    migrar_contrasenias()