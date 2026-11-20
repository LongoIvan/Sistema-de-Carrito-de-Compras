from flask import Flask

from backend.config import Config
# from backend.src.controllers.controller_carrito import carritos_bp
# from backend.src.controllers.controller_item_carrito import items_carrito_bp
from backend.src.controllers.controller_productos import productos_bp
from backend.src.controllers.controller_usuarios import usuarios_bp
from backend.src.database.database import initialize_database


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    database_url = app.config["DATABASE_URL"]
    if not database_url:
        raise RuntimeError("Define DATABASE_URL en el archivo .env antes de iniciar Flask.")

    # initialize_database(database_url)

    app.register_blueprint(usuarios_bp)
    app.register_blueprint(productos_bp)
    # app.register_blueprint(carritos_bp)
    # app.register_blueprint(items_carrito_bp)

    return app


app = create_app()
