import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Bioreplicates
        ADD position VARCHAR(100) COLLATE utf8mb4_bin,
        ADD isControl TINYINT(1) NOT NULL DEFAULT '0',
        ADD isBlank TINYINT(1) NOT NULL DEFAULT '0',
        DROP description
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Bioreplicates
        ADD description TEXT DEFAULT NULL,
        DROP position,
        DROP isControl,
        DROP isBlank
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
