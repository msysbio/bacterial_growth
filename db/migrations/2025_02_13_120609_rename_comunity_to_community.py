import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE CompartmentsPerExperiment
        CHANGE comunityId communityId VARCHAR(100) NOT NULL
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE CompartmentsPerExperiment
        CHANGE comunityUniqueId communityUniqueId INT
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Community
        CHANGE comunityId communityId VARCHAR(100) NOT NULL
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Community
        CHANGE communityId comunityId VARCHAR(100) NOT NULL
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE CompartmentsPerExperiment
        CHANGE communityUniqueId comunityUniqueId INT
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE CompartmentsPerExperiment
        CHANGE communityId comunityId VARCHAR(100) NOT NULL
    """
    conn.execute(sql.text(query))



if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
