def init_config(app):
    app.config.update(
        DEBUG=True,
        ASSETS_DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True,
        EXPLAIN_TEMPLATE_LOADING=True,
        SECRET_KEY='development_key',
    )

    return app
