import sqlalchemy as sql


def up(conn):
    query = "DROP TABLE BioReplicatesMetadata"
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Bioreplicates
        ADD description TEXT,
        ADD biosampleUrl TEXT
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Bioreplicates
        DROP description,
        DROP biosampleUrl
        ;
    """
    conn.execute(sql.text(query))

    query = """
        CREATE TABLE BioReplicatesMetadata (
            studyId varchar(100) COLLATE utf8mb4_bin NOT NULL,
            bioreplicateUniqueId int NOT NULL,
            bioreplicateId varchar(100) COLLATE utf8mb4_bin NOT NULL,
            biosampleLink text COLLATE utf8mb4_bin,
            bioreplicateDescrition text COLLATE utf8mb4_bin,
            PRIMARY KEY (studyId,bioreplicateUniqueId),
            UNIQUE KEY studyId (studyId,bioreplicateUniqueId),
            KEY fk_1 (bioreplicateUniqueId),
            CONSTRAINT BioReplicatesMetadata_fk_1
                FOREIGN KEY (bioreplicateUniqueId)
                REFERENCES Bioreplicates (id)
                ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT BioReplicatesMetadata_fk_2
                FOREIGN KEY (studyId)
                REFERENCES Study (studyId)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
