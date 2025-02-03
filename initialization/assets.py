import flask_assets


def init_assets(app):
    assets = flask_assets.Environment(app)

    assets.register('app_js', flask_assets.Bundle(
        'js/vendor/jquery-3.7.1.js',
        'js/vendor/select2-4.0.13.js',
        'js/util.js',
        'js/main.js',
        'js/search.js',
        'js/dashboard.js',
        'js/upload.js',
        'js/export.js',
        filters='rjsmin',
        output='build/app.js'
    ))

    assets.register('plotly_js', flask_assets.Bundle(
        'js/vendor/plotly-2.34.0.min.js',
        output='build/plotly.js'
    ))

    assets.register('app_css', flask_assets.Bundle(
        'css/vendor/select2-4.0.13.css',
        'css/select2-custom.css',
        'css/reset.css',
        'css/utils.css',
        'css/main.css',
        'css/sidebar.css',
        'css/search.css',
        'css/dashboard.css',
        'css/upload.css',
        'css/export.css',
        filters='cssmin',
        output='build/app.css'
    ))

    return app
