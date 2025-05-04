import simplejson as json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from db import get_config_uri, FLASK_DB

def init_flask_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = get_config_uri()
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        'json_serializer': lambda obj: json.dumps(obj, use_decimal=True),
        'json_deserializer': lambda obj: json.loads(obj, use_decimal=True),
    }

    FLASK_DB.init_app(app)

    return app
