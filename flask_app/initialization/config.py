import os

def init_config(app):
    app_env = os.getenv('APP_ENV', 'development')

    if app_env == 'development':
        app.config.update(
            DEBUG=True,
            ASSETS_DEBUG=True,
            TEMPLATES_AUTO_RELOAD=True,
            EXPLAIN_TEMPLATE_LOADING=False,
            SECRET_KEY='development_key',
        )
    elif app_env == 'test':
        app.config.update(
            DEBUG=False,
            ASSETS_DEBUG=True,
            TEMPLATES_AUTO_RELOAD=False,
            EXPLAIN_TEMPLATE_LOADING=False,
            SECRET_KEY='testing_key',
        )
    elif app_env == 'production':
        # TODO (2024-08-30) Secret key read from environment
        app.config.update(
            DEBUG=False,
            ASSETS_DEBUG=False,
            TEMPLATES_AUTO_RELOAD=False,
            EXPLAIN_TEMPLATE_LOADING=True,
            SECRET_KEY='TODO production_key',
        )
    else:
        raise KeyError(f"Unknown APP_ENV: {app_env}")

    return app
