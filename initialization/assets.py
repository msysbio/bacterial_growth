import flask_assets


def init_assets(app):
    assets = flask_assets.Environment(app)

    assets.register('app_js', flask_assets.Bundle(
        'js/vendor/jquery-3.7.1.js',
        'js/vendor/select2-4.0.13.js',
        'js/vendor/moment-2.30.1.js',
        'js/vendor/popper-core-2.11.8.js',
        'js/vendor/tippy-6.3.7.js',
        'js/upload/step1.js',
        'js/upload/step2.js',
        'js/upload/step3.js',
        'js/upload/step4.js',
        'js/util.js',
        'js/main.js',
        'js/search.js',
        'js/export.js',
        'js/study.js',
        'js/study_visualize.js',
        'js/comparison.js',
        filters='rjsmin',
        output='build/app.js'
    ))

    assets.register('plotly_js', flask_assets.Bundle(
        'js/vendor/plotly-2.34.0.min.js',
        output='build/plotly.js'
    ))

    assets.register('app_css', flask_assets.Bundle(
        'css/vendor/select2-4.0.13.css',
        'css/vendor/tippy-light-border-theme.css',
        'css/select2-custom.css',
        'css/reset.css',
        'css/utils.css',
        'css/fonts.css',
        'css/main.css',
        'css/sidebar.css',
        'css/search.css',
        'css/upload.css',
        'css/export.css',
        'css/profile.css',
        'css/study.css',
        'css/study-visualize.css',
        'css/comparison.css',
        filters='cssmin',
        output='build/app.css'
    ))

    return app
