from contextlib import closing
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection(database_url):
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)


def fetch_all(query, params=None):
    from flask import current_app

    with closing(get_connection(current_app.config["DATABASE_URL"])) as connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]


def execute_query(query, params):
    from flask import current_app

    with closing(get_connection(current_app.config["DATABASE_URL"])) as connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.rowcount


def execute_query_returning(query, params):
    from flask import current_app

    with closing(get_connection(current_app.config["DATABASE_URL"])) as connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                resultado = cursor.fetchone()
                return dict(resultado)