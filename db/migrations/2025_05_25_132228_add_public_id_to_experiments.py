import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Experiments
        ADD COLUMN publicId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
        ADD UNIQUE INDEX Experiments_publicId (publicId)
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Experiments
        DROP INDEX Experiments_publicId,
        DROP publicId
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
