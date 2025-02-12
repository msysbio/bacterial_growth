import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE BioReplicatesMetadata
        DROP PRIMARY KEY,
        ADD PRIMARY key(studyId, bioreplicateUniqueId);
    """
    params = {}
    conn.execute(sql.text(query), params)


def down(conn):
    query = """
        ALTER TABLE BioReplicatesMetadata
        DROP PRIMARY KEY,
        ADD PRIMARY key(bioreplicateId);
    """
    params = {}

    conn.execute(sql.text(query), params)


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
