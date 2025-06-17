import sqlalchemy as sql


def up(conn):
    for table in ('Project', 'Study'):
        query = f"""
            ALTER TABLE {table}
            ADD COLUMN createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
        """
        conn.execute(sql.text(query))

        query = f"""
            ALTER TABLE {table}
            ADD COLUMN updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        """
        conn.execute(sql.text(query))


def down(conn):
    for table in ('Project', 'Study'):
        for column in ('createdAt', 'updatedAt'):
            query = f"ALTER TABLE {table} DROP COLUMN {column}"
            conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
