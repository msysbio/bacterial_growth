import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Study
        ADD COLUMN ownerUniqueID varchar(100) COLLATE utf8mb4_bin DEFAULT NULL
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Project
        ADD COLUMN ownerUniqueID varchar(100) COLLATE utf8mb4_bin DEFAULT NULL
    """
    conn.execute(sql.text(query))


def down(conn):
    query = "ALTER TABLE Study DROP COLUMN ownerUniqueID"
    conn.execute(sql.text(query))

    query = "ALTER TABLE Project DROP COLUMN ownerUniqueID"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
