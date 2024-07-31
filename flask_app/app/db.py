import os
import tomllib
from pathlib import Path

import sqlalchemy


def _create_engine():
    config = get_config()

    username = config.pop('username', '')
    password = config.pop('password', '')
    host = config.pop('host', 'localhost')
    port = config.pop('port', '3306')
    database = config.pop('database')

    return sqlalchemy.create_engine(
        f"mysql+mysqldb://{username}:{password}@{host}:3306/{database}",
        connect_args=config,
    )


def get_config():
    env = os.getenv('APP_ENV', 'development')
    return tomllib.loads(Path('config/database.toml').read_text())[env]


def get_connection():
    return DB.connect()

DB = _create_engine()
