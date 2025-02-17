import os
import tomllib
from pathlib import Path

import sqlalchemy
import sqlalchemy.orm as orm


def _create_engine():
    config = get_config()

    username = config.pop('username', '')
    password = config.pop('password', '')
    host     = config.pop('host', 'localhost')
    port     = config.pop('port', '3306')
    database = config.pop('database')

    engine = sqlalchemy.create_engine(
        f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}",
        connect_args=config,
        # Set echo=True for full query logging:
        echo=False,
    )

    return engine


def get_config():
    env = os.getenv('APP_ENV', 'development')
    return tomllib.loads(Path('db/config.toml').read_text())[env]


def get_connection():
    return DB.connect()


def get_session():
    return orm.Session(DB)


def get_transaction():
    return DB.begin()


DB = _create_engine()
