import flask_assets


def init_assets(app):
    assets = flask_assets.Environment(app)

    assets.register('app_js', flask_assets.Bundle(
        'js/vendor/jquery-3.7.1.js',
        'js/util.js',
        'js/main.js',
        'js/search.js',
        'js/dashboard.js',
        filters='rjsmin',
        output='build/app.js'
    ))

    assets.register('plotly_js', flask_assets.Bundle(
        'js/vendor/plotly-2.34.0.min.js',
        output='build/plotly.js'
    ))

    assets.register('app_css', flask_assets.Bundle(
        'css/reset.css',
        'css/utils.css',
        'css/main.css',
        'css/sidebar.css',
        'css/search.css',
        'css/dashboard.css',
        filters='cssmin',
        output='build/app.css'
    ))

    return app
