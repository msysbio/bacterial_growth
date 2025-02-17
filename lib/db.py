import sqlalchemy as sql


def get_primary_key_name(db_conn, table_name):
    # Get the name of the primary key field
    query = f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'"
    result = db_conn.execute(sql.text(query)).one()
    return result[4]
