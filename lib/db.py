import sqlalchemy as sql
import sqlalchemy.dialects.mysql as mysql
import pandas as pd


def execute_text(db_conn, text, **params):
    return db_conn.execute(sql.text(text), params)


def execute_into_df(db_conn, query):
    if isinstance(db_conn, sql.orm.Session):
        db_conn = db_conn.connection()

    statement = query.compile(dialect=mysql.dialect())
    return pd.read_sql(statement, db_conn)
