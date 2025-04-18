import os


def init_config(app):
    """
    Configuration reference: <https://flask.palletsprojects.com/en/stable/config/>
    """
    app_env   = os.getenv('APP_ENV', 'development')
    log_level = os.getenv('LOG_LEVEL', None)
    timing    = os.getenv('TIME')

    # 200MiB max size
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

    if app_env == 'development':
        app.config.update(
            DEBUG=True,
            ASSETS_DEBUG=False,
            TEMPLATES_AUTO_RELOAD=True,
            EXPLAIN_TEMPLATE_LOADING=False,
            SECRET_KEY='development_key',
        )
    elif app_env == 'test':
        app.config.update(
            DEBUG=False,
            ASSETS_DEBUG=False,
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
            SESSION_COOKIE_SECURE=True,
        )
    else:
        raise KeyError(f"Unknown APP_ENV: {app_env}")

    if log_level:
        app.logger.setLevel(log_level.upper())

    if timing:
        app.logger.getChild('timing').setLevel('INFO')

    return app
