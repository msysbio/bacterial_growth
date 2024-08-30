from jinja2.environment import Template

from flask import Flask

from flask_app.initialization.config import init_config
from flask_app.initialization.assets import init_assets
from flask_app.initialization.routes import init_routes


def create_app():
    app = Flask(__name__)

    app = init_config(app)
    app = init_assets(app)
    app = init_routes(app)

    return app


if __name__ == "__main__":
    app = create_app()

    app.run(host="0.0.0.0", port=8080)
