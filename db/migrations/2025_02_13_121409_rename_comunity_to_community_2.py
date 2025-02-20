import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Community
        CHANGE comunityUniqueId communityUniqueId INT NOT NULL AUTO_INCREMENT
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Community
        RENAME KEY comunityId TO communityId
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Community
        RENAME KEY communityId TO comunityId
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Community
        CHANGE communityUniqueId comunityUniqueId INT NOT NULL AUTO_INCREMENT
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
