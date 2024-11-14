import os
import tomllib
from pathlib import Path

import sqlalchemy


def _create_engine():
    config = get_config()

    username = config.pop('username', '')
    password = config.pop('password', None)
    host     = config.pop('host', 'localhost')
    port     = config.pop('port', '3306')
    database = config.pop('database')

    if password is None:
        connection_string = f"mysql+pymysql://{username}@{host}:{port}/{database}"
    else:
        connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

    engine = sqlalchemy.create_engine(
        connection_string,
        connect_args=config,
        # Set echo=True for full query logging:
        echo=False,
    )

    return engine


def get_config():
    env = os.getenv('APP_ENV', 'development')
    return tomllib.loads(Path('config/database.toml').read_text())[env]


def get_connection():
    return DB.connect()


DB = _create_engine()
