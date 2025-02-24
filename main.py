import os

from flask import Flask

from initialization.config import init_config
from initialization.assets import init_assets
from initialization.routes import init_routes, dump_routes
from initialization.plotly import init_plotly
from initialization.timing import init_timing


def create_app(env):
    app = Flask(__name__)

    app = init_config(app)
    app = init_assets(app)
    app = init_routes(app)

    init_plotly()

    if env == 'development' or os.getenv('TIME'):
        app = init_timing(app)

    if env == 'development':
        dump_routes(app.url_map.iter_rules(), '.routes.json')

    return app


if __name__ == "__main__":
    env = os.getenv('APP_ENV', 'development')
    app = create_app(env)

    app.run(host="0.0.0.0", port=8081)
