from contextlib import closing
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection(database_url):
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)


def initialize_database(database_url):
    statements = (
        """
            CREATE TABLE IF NOT EXISTS usuario (
                idusuario INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                mail TEXT NOT NULL,
                contrasenia TEXT NOT NULL,
                rol TEXT NOT NULL
            )
        """,
        """
            CREATE TABLE IF NOT EXISTS producto (
                idproducto INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                precio DOUBLE PRECISION NOT NULL,
                stock INTEGER NOT NULL DEFAULT 1,
                categoria TEXT NOT NULL,
                fecha DATE NOT NULL,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                descripcion TEXT NOT NULL
            )
        """,
        """
            CREATE TABLE IF NOT EXISTS carrito (
                idcarrito INTEGER PRIMARY KEY,
                idusuario INTEGER NOT NULL,
                fecha DATE NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Pendiente'
            )
        """,
        """
            CREATE TABLE IF NOT EXISTS item_carrito (
                id_item_carrito INTEGER PRIMARY KEY,
                idcarrito INTEGER NOT NULL,
                id_item_producto INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario DOUBLE PRECISION NOT NULL,
                CONSTRAINT fk_item_carrito_carrito
                    FOREIGN KEY (idcarrito) REFERENCES carrito (idcarrito)
            )
        """,
        """
            ALTER TABLE item_carrito
            ADD COLUMN IF NOT EXISTS idcarrito INTEGER
        """,
        """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'fk_item_carrito_carrito'
                      AND conrelid = 'item_carrito'::regclass
                ) THEN
                    ALTER TABLE item_carrito
                    ADD CONSTRAINT fk_item_carrito_carrito
                    FOREIGN KEY (idcarrito) REFERENCES carrito (idcarrito);
                END IF;
            END;
            $$
        """,
    )

    with closing(get_connection(database_url)) as connection:
        with connection:
            with connection.cursor() as cursor:
                for statement in statements:
                    cursor.execute(statement)


def fetch_all(query):
    from flask import current_app

    with closing(get_connection(current_app.config["DATABASE_URL"])) as connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]

def execute_query(query, params):
    from flask import current_app

    with closing(get_connection(current_app.config["DATABASE_URL"])) as connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.rowcount