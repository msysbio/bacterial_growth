import os


def init_config(app):
    """
    Configuration reference: <https://flask.palletsprojects.com/en/stable/config/>
    """
    app_env   = os.getenv('APP_ENV', 'development')
    log_level = os.getenv('LOG_LEVEL', None)
    timing    = os.getenv('TIME')

    # Load env variables starting with "FLASK_" into the config
    app.config.from_prefixed_env()

    # 200MiB max size
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

    if app_env == 'development':
        app.config.update(
            DEBUG=True,
            ASSETS_DEBUG=False,
            TEMPLATES_AUTO_RELOAD=True,
            EXPLAIN_TEMPLATE_LOADING=False,
        )
    elif app_env == 'test':
        app.config.update(
            DEBUG=False,
            ASSETS_DEBUG=False,
            TEMPLATES_AUTO_RELOAD=False,
            EXPLAIN_TEMPLATE_LOADING=False,
        )
    elif app_env == 'production':
        app.config.update(
            DEBUG=False,
            ASSETS_DEBUG=False,
            TEMPLATES_AUTO_RELOAD=False,
            EXPLAIN_TEMPLATE_LOADING=True,
            SESSION_COOKIE_SECURE=True,
        )
    else:
        raise KeyError(f"Unknown APP_ENV: {app_env}")

    if log_level:
        app.logger.setLevel(log_level.upper())

    if timing:
        app.logger.getChild('timing').setLevel('INFO')

    return app
