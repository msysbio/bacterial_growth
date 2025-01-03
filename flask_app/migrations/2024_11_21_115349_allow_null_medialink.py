import sqlalchemy as sql

def up(conn):
    query = """
        ALTER TABLE Compartments
        MODIFY COLUMN mediaLink
        VARCHAR(100);
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Compartments
        MODIFY COLUMN mediaLink
        VARCHAR(100) NOT NULL;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from flask_app.lib.migrations import run
    run(__file__, up, down)
