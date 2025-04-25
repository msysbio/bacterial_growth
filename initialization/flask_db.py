from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from db import get_config_uri, FLASK_DB

def init_flask_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = get_config_uri()

    FLASK_DB.init_app(app)

    return app
