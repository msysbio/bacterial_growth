import os

from dotenv import load_dotenv


def init_config(app):
    """
    Configuration reference: <https://flask.palletsprojects.com/en/stable/config/>
    """
    app_env   = os.getenv('APP_ENV', 'development')
    log_level = os.getenv('LOG_LEVEL', None)
    timing    = os.getenv('TIME')

    # Load .env file from local directory
    load_dotenv('.env')

    # Load env variables starting with "MGROWTHDB_" into the config
    app.config.from_prefixed_env('MGROWTHDB')

    # 200MiB max size
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    if app_env == 'development':
        app.config.update(
            DEBUG=True,
            ASSETS_DEBUG=False,
            SQLALCHEMY_RECORD_QUERIES=True,
            TEMPLATES_AUTO_RELOAD=True,
            EXPLAIN_TEMPLATE_LOADING=False,
        )
    elif app_env == 'test':
        app.config.update(
            DEBUG=False,
            ASSETS_DEBUG=False,
            TEMPLATES_AUTO_RELOAD=False,
            EXPLAIN_TEMPLATE_LOADING=False,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY='testing_key',
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
