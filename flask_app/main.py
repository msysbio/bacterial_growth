from flask import Flask
import flask_app.app.views as views


def create_app():
    app = Flask(__name__)

    app.config.update(
        DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True,
        EXPLAIN_TEMPLATE_LOADING=True,
    )

    app.add_url_rule("/",      view_func=views.index)
    app.add_url_rule("/about", view_func=views.about)

    return app


if __name__ == "__main__":
    app = create_app()

    app.run(host="0.0.0.0", port=8080)
