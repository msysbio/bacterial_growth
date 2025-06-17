import os

from flask import Flask

from initialization.config import init_config
from initialization.flask_db import init_flask_db
from initialization.assets import init_assets
from initialization.routes import init_routes, dump_routes
from initialization.plotly import init_plotly
from initialization.timing import init_timing
from initialization.global_handlers import init_global_handlers
from initialization.template_filters import init_template_filters
from initialization.admin import init_admin
from initialization.celery import init_celery


def create_app():
    env = os.getenv('APP_ENV', 'development')
    app = Flask(
        __name__,
        template_folder="app/view/templates",
        static_folder="app/view/static"
    )

    app = init_config(app)
    app = init_flask_db(app)
    app = init_assets(app)
    app = init_routes(app)
    app = init_global_handlers(app)
    app = init_template_filters(app)
    app = init_admin(app)
    app = init_celery(app)

    init_plotly()

    if env == 'development' or os.getenv('TIME'):
        app = init_timing(app)

    if env == 'development':
        dump_routes(app.url_map.iter_rules(), '.routes.json')

    return app


if __name__ == "__main__":
    app = create_app()

    app.run(host="0.0.0.0", port=8081)
