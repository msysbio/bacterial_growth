import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE BioReplicatesPerExperiment
        CHANGE bioreplicateId name VARCHAR(100) COLLATE utf8mb4_bin NOT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE BioReplicatesPerExperiment
        CHANGE bioreplicateUniqueId id INT NOT NULL AUTO_INCREMENT,
        DROP experimentId,
        DROP controls,
        DROP OD,
        DROP OD_std,
        DROP Plate_counts,
        DROP Plate_counts_std,
        DROP pH
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE BioReplicatesPerExperiment
        CHANGE experimentUniqueId experimentId INT NOT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = "RENAME TABLE BioReplicatesPerExperiment to Bioreplicates"
    conn.execute(sql.text(query))


def down(conn):
    query = "RENAME TABLE Bioreplicates to BioReplicatesPerExperiment"
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE BioReplicatesPerExperiment
        CHANGE experimentId experimentUniqueId INT NOT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE BioReplicatesPerExperiment
        CHANGE id bioreplicateUniqueId INT NOT NULL AUTO_INCREMENT,
        ADD pH tinyint(1) DEFAULT '0',
        ADD Plate_counts_std tinyint(1) DEFAULT '0',
        ADD Plate_counts tinyint(1) DEFAULT '0',
        ADD OD_std tinyint(1) DEFAULT '0',
        ADD OD tinyint(1) DEFAULT '0',
        ADD controls tinyint(1) DEFAULT '0',
        ADD experimentId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE BioReplicatesPerExperiment
        CHANGE name bioreplicateId VARCHAR(100) COLLATE utf8mb4_bin NOT NULL
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
