import sqlalchemy as sql


def get_primary_key_names(db_conn, table_name):
    # Get the name of the primary key field
    query = f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'"
    result = [row[4] for row in db_conn.execute(sql.text(query)).all()]
    return result


def execute_text(db_conn, text, **params):
    return db_conn.execute(sql.text(text), params)
