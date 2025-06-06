from flask_debugtoolbar import DebugToolbarExtension


def init_debug_toolbar(app):
    DebugToolbarExtension(app)

    return app
