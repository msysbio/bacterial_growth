import flask_assets

def init_assets(app):
    assets = flask_assets.Environment(app)

    javascripts = flask_assets.Bundle(
        'js/vendor/jquery-3.7.1.js',
        'js/vendor/plotly-2.34.0.min.js',
        'js/util.js',
        'js/main.js',
        'js/search.js',
        'js/dashboard.js',
        filters='jsmin',
        output='build/bundle.js'
    )
    assets.register('js_bundle', javascripts)

    stylesheets = flask_assets.Bundle(
        'css/reset.css',
        'css/utils.css',
        'css/main.css',
        'css/sidebar.css',
        'css/search.css',
        'css/dashboard.css',
        filters='cssmin',
        output='build/bundle.css'
    )
    assets.register('css_bundle', stylesheets)

    return app
