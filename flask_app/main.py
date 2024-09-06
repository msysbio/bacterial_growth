import os

from jinja2.environment import Template
from flask import Flask

from flask_app.initialization.config import init_config
from flask_app.initialization.assets import init_assets
from flask_app.initialization.routes import init_routes
from flask_app.initialization.timing import init_timing


def create_app(env):
    app = Flask(__name__)

    app = init_config(app)
    app = init_assets(app)
    app = init_routes(app)

    if env == 'development' or os.getenv('TIME'):
        app = init_timing(app)

    return app


if __name__ == "__main__":
    env = os.getenv('APP_ENV', 'development')
    app = create_app(env)

    app.run(host="0.0.0.0", port=8080)
